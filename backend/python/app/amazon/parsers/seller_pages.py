"""从 Seller Central 各页面提取结构化数据。"""
from __future__ import annotations

import re
from typing import Any


EXTRACT_PERFORMANCE_TABLE_JS = """
() => {
  const money = (value) => {
    const match = String(value || '').replace(/,/g, '').match(/(?:US?\\$|€|£|¥)?\\s*([\\d]+(?:\\.\\d+)?)/i);
    if (!match) return '';
    const num = parseFloat(match[1]);
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const integer = (value) => {
    const match = String(value || '').replace(/,/g, '').match(/(\\d+)/);
    return match ? match[1] : '0';
  };
  const percent = (value) => {
    const match = String(value || '').match(/([\\d.]+)\\s*%/);
    return match ? match[1] : '';
  };
  const STATUS_ONLY = /^(在售|停售|缺货|active|inactive|out of stock|–|-)$/i;
  const UI_ACTION = /^(了解更多|创建\\s*A\\/?B\\s*试验|查看建议|编辑未来|报告缺失|learn more|create a\\/?b test|view suggestion|edit future|report missing)/i;
  const asinFromCell = (td, text) => {
    const href = td?.querySelector?.('a')?.href || '';
    const blob = `${href} ${text || ''}`;
    const match = blob.match(/\\b([A-Z0-9]{10})\\b/i);
    if (!match) return '';
    const asin = match[1].toUpperCase();
    if (/^G\\d{9}$/.test(asin)) return '';
    return /[0-9]/.test(asin) ? asin : '';
  };
  const titleFromCell = (td) => {
    if (!td) return '';
    const link = td.querySelector('a');
    if (link) {
      const linked = (link.getAttribute('title') || link.innerText || '').trim();
      if (linked.length > 4 && !STATUS_ONLY.test(linked) && !UI_ACTION.test(linked)) return linked;
    }
    const text = (td.innerText || '').trim();
    if (!text || STATUS_ONLY.test(text) || UI_ACTION.test(text)) return '';
    if (/^US?\\$\\s*[\\d,]+(?:\\.\\d+)?$/i.test(text)) return '';
    return text;
  };
  const headerRules = [
    { key: 'product_name', pattern: /(title|商品名称|商品名|父商品|子商品|product name)/i },
    { key: 'asin', pattern: /asin/i },
    { key: 'sku', pattern: /sku/i },
    { key: 'revenue_30d', pattern: /(ordered product sales|已订购商品销售额|销售额(?!占比)|ordered sales)/i },
    { key: 'orders_30d', pattern: /(units ordered|已订购数量|订单量|ordered units|销量)/i },
    { key: 'page_views', pattern: /(sessions|会话|page views|浏览量|页面浏览量)/i },
    { key: 'ad_spend_30d', pattern: /(spend|广告花费|广告支出|ad spend)/i },
    { key: 'acos', pattern: /acos/i },
    { key: 'tacos', pattern: /tacos/i },
    { key: 'conversion_rate', pattern: /(conversion|转化率|unit session|子商品转化率)/i },
    { key: 'inventory', pattern: /(inventory|库存|available)/i },
  ];
  const scoreTable = (headers) => {
    const headerText = headers.join(' ').toLowerCase();
    let score = 0;
    if (/child asin|子\\s*asin|\(child\)/i.test(headerText)) score += 4;
    if (/asin/i.test(headerText)) score += 4;
    if (/ordered product sales|已订购商品销售额/i.test(headerText)) score += 3;
    if (/units ordered|已订购数量|订单量/i.test(headerText)) score += 2;
    if (/sessions|会话/i.test(headerText)) score += 1;
    if (/status|状态/i.test(headerText) && !/asin/i.test(headerText)) score -= 3;
    if (/销售额|sales/i.test(headerText) && !/asin/i.test(headerText)) score -= 1;
    return score;
  };
  const collectRoots = (node, out = []) => {
    if (!node) return out;
    out.push(node);
    if (node.shadowRoot) collectRoots(node.shadowRoot, out);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) collectRoots(el.shadowRoot, out);
    });
    return out;
  };
  const collectTables = () => {
    const tables = [];
    const seen = new Set();
    for (const root of collectRoots(document)) {
      root.querySelectorAll('table').forEach((table) => {
        if (seen.has(table)) return;
        seen.add(table);
        tables.push(table);
      });
    }
    return tables;
  };
  const buildColumnMap = (headers) => {
    const columnMap = {};
    headers.forEach((label, index) => {
      for (const rule of headerRules) {
        if (rule.pattern.test(label) && columnMap[rule.key] == null) {
          columnMap[rule.key] = index;
          break;
        }
      }
    });
    return columnMap;
  };
  const pushProductRow = (rows, seen, payload) => {
    const asin = String(payload.asin || '').toUpperCase();
    if (!asin || seen.has(asin)) return;
    let productName = String(payload.product_name || '').trim();
    if (UI_ACTION.test(productName)) return;
    if (!productName || STATUS_ONLY.test(productName)) productName = asin;
    if (UI_ACTION.test(productName)) return;
    seen.add(asin);
    rows.push({
      rank_no: rows.length + 1,
      product_name: productName.slice(0, 180),
      asin,
      sku: payload.sku || '',
      revenue_30d: payload.revenue_30d || '',
      orders_30d: payload.orders_30d || '0',
      page_views: payload.page_views || '0',
      ad_spend_30d: payload.ad_spend_30d || '',
      acos: payload.acos || '',
      tacos: payload.tacos || '',
      conversion_rate: payload.conversion_rate || '',
      inventory: payload.inventory || '0',
      currency: 'USD',
    });
  };
  const parseBodyRow = (tds, cells, columnMap, rows, seen) => {
    if (!cells.length) return;
    let asin = '';
    let productName = '';
    tds.forEach((td) => {
      const fromCell = asinFromCell(td, td.innerText || '');
      if (fromCell) asin = fromCell;
      const title = titleFromCell(td);
      if (title.length > productName.length) productName = title;
    });
    if (columnMap.asin != null && tds[columnMap.asin]) {
      const fromCol = asinFromCell(tds[columnMap.asin], cells[columnMap.asin]);
      if (fromCol) asin = fromCol;
    }
    if (columnMap.product_name != null && tds[columnMap.product_name]) {
      const fromCol = titleFromCell(tds[columnMap.product_name]);
      if (fromCol) productName = fromCol;
    }
    if (!asin) return;
    pushProductRow(rows, seen, {
      asin,
      product_name: productName,
      sku: columnMap.sku != null ? cells[columnMap.sku].slice(0, 80) : '',
      revenue_30d: columnMap.revenue_30d != null ? money(cells[columnMap.revenue_30d]) : '',
      orders_30d: columnMap.orders_30d != null ? integer(cells[columnMap.orders_30d]) : '0',
      page_views: columnMap.page_views != null ? integer(cells[columnMap.page_views]) : '0',
      ad_spend_30d: columnMap.ad_spend_30d != null ? money(cells[columnMap.ad_spend_30d]) : '',
      acos: columnMap.acos != null ? percent(cells[columnMap.acos]) : '',
      tacos: columnMap.tacos != null ? percent(cells[columnMap.tacos]) : '',
      conversion_rate: columnMap.conversion_rate != null ? percent(cells[columnMap.conversion_rate]) : '',
      inventory: columnMap.inventory != null ? integer(cells[columnMap.inventory]) : '0',
    });
  };

  const rows = [];
  const seen = new Set();
  const hasMetrics = (row) => !!(row.revenue_30d || (row.orders_30d && row.orders_30d !== '0') || (row.page_views && row.page_views !== '0'));
  const rankedTables = collectTables()
    .map((table) => {
      const headerCells = Array.from(table.querySelectorAll('thead th, tr th, tr:first-child td'));
      const headers = headerCells.map((cell) => (cell.innerText || '').trim()).filter(Boolean);
      return { table, headers, score: scoreTable(headers) };
    })
    .filter((item) => item.headers.length && item.score >= 2)
    .sort((a, b) => b.score - a.score);

  let bestRows = [];
  let bestScore = -1;
  for (const { table, headers } of rankedTables) {
    const columnMap = buildColumnMap(headers);
    const tableRows = [];
    const tableSeen = new Set();
    table.querySelectorAll('tbody tr, [role="row"]').forEach((tr) => {
      if (tr.querySelector('th,[role="columnheader"]')) return;
      const tds = Array.from(tr.querySelectorAll('td, [role="gridcell"]'));
      const cells = tds.map((td) => (td.innerText || '').trim());
      parseBodyRow(tds, cells, columnMap, tableRows, tableSeen);
    });
    const metricCount = tableRows.filter(hasMetrics).length;
    const score = metricCount * 100 + tableRows.length;
    if (score > bestScore) {
      bestScore = score;
      bestRows = tableRows;
    }
  }

  if (!bestRows.some(hasMetrics)) {
    for (const root of collectRoots(document)) {
      for (const grid of root.querySelectorAll('[role="grid"], kat-table, kat-table-body')) {
        const headerCells = Array.from(
          grid.querySelectorAll('[role="columnheader"], thead th, tr th, tr:first-child td, [role="row"]:first-child [role="gridcell"], [role="row"]:first-child td')
        );
        const headers = headerCells.map((cell) => (cell.innerText || '').trim()).filter(Boolean);
        if (scoreTable(headers) < 2) continue;
        const columnMap = buildColumnMap(headers);
        const gridRows = [];
        const gridSeen = new Set();
        grid.querySelectorAll('[role="row"], tbody tr').forEach((tr, index) => {
          if (index === 0 && headers.length && tr.querySelector('[role="columnheader"], th')) return;
          const tds = Array.from(tr.querySelectorAll('[role="gridcell"], td, th'));
          const cells = tds.map((td) => (td.innerText || '').trim());
          parseBodyRow(tds, cells, columnMap, gridRows, gridSeen);
        });
        const metricCount = gridRows.filter(hasMetrics).length;
        const score = metricCount * 100 + gridRows.length;
        if (score > bestScore) {
          bestScore = score;
          bestRows = gridRows;
        }
      }
    }
  }

  return bestRows.slice(0, 100);
}
"""

EXTRACT_BUSINESS_REPORT_JS = EXTRACT_PERFORMANCE_TABLE_JS
EXTRACT_PRODUCTS_JS = EXTRACT_BUSINESS_REPORT_JS

EXTRACT_INVENTORY_JS = """
() => {
  const STATUS_ONLY = /^(在售|停售|缺货|active|inactive|out of stock|–|-)$/i;
  const asinFrom = (text) => {
    const blob = String(text || '');
    const fromUrl = blob.match(/(?:\\/dp\\/|\\/gp\\/product\\/|asin=)([A-Z0-9]{10})/i);
    if (fromUrl) return fromUrl[1].toUpperCase();
    const match = blob.match(/\\b([A-Z0-9]{10})\\b/i);
    if (!match) return '';
    const asin = match[1].toUpperCase();
    if (/^G\\d{9}$/.test(asin)) return '';
    return /[0-9]/.test(asin) ? asin : '';
  };
  const integer = (value) => {
    const match = String(value || '').replace(/,/g, '').match(/(\\d+)/);
    return match ? match[1] : '0';
  };
  const collectRoots = (node, out = []) => {
    if (!node) return out;
    out.push(node);
    if (node.shadowRoot) collectRoots(node.shadowRoot, out);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) collectRoots(el.shadowRoot, out);
    });
    return out;
  };
  const headerRules = [
    { key: 'asin', pattern: /asin/i },
    { key: 'sku', pattern: /sku/i },
    { key: 'product_name', pattern: /(title|商品|product name)/i },
    { key: 'inventory', pattern: /(available|可售|available quantity|inventory|库存|in stock|fba)/i },
  ];
  const rows = [];
  const seen = new Set();
  const pushRow = (payload) => {
    const asin = String(payload.asin || '').toUpperCase();
    if (!asin || seen.has(asin)) return;
    seen.add(asin);
    rows.push({
      rank_no: rows.length + 1,
      product_name: String(payload.product_name || asin).slice(0, 180),
      asin,
      sku: payload.sku || '',
      revenue_30d: '',
      orders_30d: '0',
      page_views: '0',
      ad_spend_30d: '',
      acos: '',
      tacos: '',
      conversion_rate: '',
      inventory: payload.inventory || '0',
      currency: 'USD',
    });
  };
  for (const root of collectRoots(document)) {
    for (const table of root.querySelectorAll('table, [role="grid"]')) {
      const headerCells = Array.from(
        table.querySelectorAll('thead th, tr th, [role="columnheader"], tr:first-child td')
      );
      const headers = headerCells.map((cell) => (cell.innerText || '').trim()).filter(Boolean);
      if (!headers.length) continue;
      const headerText = headers.join(' ');
      if (!/(asin|sku|title|商品|inventory|库存)/i.test(headerText)) continue;
      const columnMap = {};
      headers.forEach((label, index) => {
        for (const rule of headerRules) {
          if (rule.pattern.test(label) && columnMap[rule.key] == null) {
            columnMap[rule.key] = index;
            break;
          }
        }
      });
      table.querySelectorAll('tbody tr, [role="row"]').forEach((tr) => {
        if (tr.querySelector('th,[role="columnheader"]')) return;
        const tds = Array.from(tr.querySelectorAll('td, [role="gridcell"]'));
        const cells = tds.map((td) => (td.innerText || '').trim());
        if (!cells.length) return;
        let asin = '';
        let productName = '';
        let inventory = '0';
        tds.forEach((td, index) => {
          const cell = cells[index] || '';
          const href = td.querySelector('a')?.href || '';
          const found = asinFrom(`${href} ${cell}`);
          if (found) asin = found;
          if (cell.length > 8 && !STATUS_ONLY.test(cell) && !asinFrom(cell)) productName = cell;
        });
        if (columnMap.asin != null && cells[columnMap.asin]) {
          const fromCol = asinFrom(cells[columnMap.asin]);
          if (fromCol) asin = fromCol;
        }
        if (columnMap.product_name != null && cells[columnMap.product_name]) {
          productName = cells[columnMap.product_name];
        }
        if (columnMap.inventory != null && cells[columnMap.inventory]) {
          inventory = integer(cells[columnMap.inventory]);
        } else {
          const nums = cells.map((cell) => integer(cell)).filter((n) => n !== '0');
          if (nums.length) inventory = nums[nums.length - 1];
        }
        if (columnMap.sku != null && cells[columnMap.sku]) {
          pushRow({ asin, product_name: productName, sku: cells[columnMap.sku].slice(0, 80), inventory });
          return;
        }
        if (asin) pushRow({ asin, product_name: productName, inventory });
      });
      if (rows.length) break;
    }
    if (rows.length) break;
  }
  return rows.slice(0, 80);
}
"""

EXTRACT_INVENTORY_CARDS_JS = """
() => {
  const asinRe = /^[A-Z0-9]{10}$/i;
  const b0Re = /\\b(B0[A-Z0-9]{8})\\b/i;
  const money = (raw) => {
    const match = String(raw || '').replace(/,/g, '').match(/(?:US?\\$|USD)?\\s*([\\d]+(?:\\.\\d+)?)/i);
    if (!match) return '';
    const num = parseFloat(match[1]);
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const integer = (raw) => {
    const match = String(raw || '').replace(/,/g, '').match(/(\\d+)/);
    return match ? match[1] : '0';
  };
  const labelRules = [
    [/^(可售|available)$/i, 'inventory'],
    [/^(在库|on hand|on-hand)$/i, 'on_hand'],
    [/^(FBA\\s*可售|available\\s*\\(fba\\)|fulfillable)$/i, 'inventory'],
    [/^(页面浏览量|page views?|sessions?)$/i, 'page_views'],
    [/^(售出件数|units sold|ordered units|销量)$/i, 'orders_30d'],
    [/^(销售额|sales)$/i, 'revenue_30d'],
    [/^(可售数量|available quantity)$/i, 'inventory_alt'],
  ];
  const isAsinLine = (line) => {
    if (!asinRe.test(line)) return false;
    const asin = line.toUpperCase();
    return /[0-9]/.test(asin) && !/^G\\d{9}$/.test(asin);
  };
  const parseMetricsFromLines = (lines) => {
    const metrics = {};
    for (let j = 0; j < lines.length; j += 1) {
      for (const [pattern, key] of labelRules) {
        if (!pattern.test(lines[j])) continue;
        const next = lines[j + 1] || '';
        if (next === '--' || next === '—') continue;
        if (key === 'revenue_30d') {
          const value = money(next) || money(lines[j]);
          if (value) metrics[key] = value;
        } else {
          metrics[key] = integer(next);
        }
      }
      const inlineRevenue = lines[j].match(/US\\$\\s*([\\d,]+(?:\\.\\d+)?)/i);
      if (inlineRevenue && !metrics.revenue_30d) {
        metrics.revenue_30d = money(inlineRevenue[1]);
      }
    }
    metrics.inventory = metrics.inventory || metrics.inventory_alt || metrics.on_hand || '0';
    return metrics;
  };
  const pickCardRoot = (node) => {
    let current = node;
    for (let depth = 0; depth < 8 && current; depth += 1) {
      const tag = (current.tagName || '').toLowerCase();
      if (['article', 'section', 'li', 'tr', 'kat-card'].includes(tag)) return current;
      const cls = String(current.className || '');
      if (/card|inventory|product|row|item/i.test(cls)) return current;
      current = current.parentElement;
    }
    return node.parentElement?.parentElement || node;
  };
  const upsert = (map, asin, payload) => {
    const current = map.get(asin) || {};
    const merged = { ...current, ...payload, asin };
    ['inventory', 'page_views', 'orders_30d', 'revenue_30d'].forEach((key) => {
      const nextVal = parseFloat(String(payload[key] || '0').replace(/,/g, '')) || 0;
      const curVal = parseFloat(String(current[key] || '0').replace(/,/g, '')) || 0;
      if (nextVal >= curVal && payload[key] != null) merged[key] = payload[key];
    });
    const curName = String(current.product_name || '');
    const nextName = String(payload.product_name || '');
    if (nextName.length > curName.length) merged.product_name = nextName;
    map.set(asin, merged);
  };
  const map = new Map();

  document.querySelectorAll('[class*="tableContentRow"], [class*="TableContentRow"]').forEach((rowEl) => {
    const lines = (rowEl.innerText || '').split('\\n').map((s) => s.trim()).filter(Boolean);
    let asin = '';
    for (let i = 0; i < lines.length - 1; i += 1) {
      if (/^asin$/i.test(lines[i]) && b0Re.test(lines[i + 1])) {
        asin = lines[i + 1].toUpperCase();
        break;
      }
    }
    if (!asin) {
      const inline = lines.join(' ').match(/\\b(B0[A-Z0-9]{8})\\b/i);
      if (inline) asin = inline[1].toUpperCase();
    }
    if (!asin) return;
    const productName = lines.find((line) => line.length > 24 && !/^asin$|^sku$/i.test(line)) || asin;
    const metrics = parseMetricsFromLines(lines);
    upsert(map, asin, { product_name: productName, ...metrics });
  });

  document.querySelectorAll('a[href*="/dp/"], a[href*="asin="]').forEach((anchor) => {
    const href = anchor.href || '';
    const match = href.match(/\\/dp\\/(B0[A-Z0-9]{8})/i) || href.match(/asin=(B0[A-Z0-9]{8})/i);
    if (!match) return;
    const asin = match[1].toUpperCase();
    const card = pickCardRoot(anchor);
    const lines = (card?.innerText || anchor.innerText || '').split('\\n').map((s) => s.trim()).filter(Boolean);
    const productName = (anchor.getAttribute('title') || anchor.innerText || '').trim();
    const metrics = parseMetricsFromLines(lines);
    upsert(map, asin, {
      product_name: productName || asin,
      ...metrics,
    });
  });

  const lines = (document.body.innerText || '').split('\\n').map((s) => s.trim()).filter(Boolean);
  for (let i = 0; i < lines.length; i += 1) {
    if (!isAsinLine(lines[i])) continue;
    const asin = lines[i].toUpperCase();
    if (map.has(asin)) continue;
    let productName = '';
    for (let j = Math.max(0, i - 6); j < i; j += 1) {
      if (lines[j].length > 18 && !/^ASIN$/i.test(lines[j]) && !isAsinLine(lines[j])) {
        productName = lines[j];
      }
    }
    const windowLines = lines.slice(i + 1, Math.min(lines.length, i + 45));
    const metrics = parseMetricsFromLines(windowLines);
    upsert(map, asin, {
      product_name: productName || asin,
      ...metrics,
    });
  }

  return [...map.values()].slice(0, 120).map((row, index) => ({
    rank_no: index + 1,
    product_name: String(row.product_name || row.asin || '').slice(0, 180),
    asin: row.asin,
    sku: row.sku || '',
    revenue_30d: row.revenue_30d || '',
    orders_30d: row.orders_30d || '0',
    page_views: row.page_views || '0',
    ad_spend_30d: '',
    acos: '',
    tacos: '',
    conversion_rate: '',
    inventory: row.inventory || '0',
    currency: 'USD',
  }));
}
"""

EXTRACT_CATALOG_JS = """
() => {
  const STATUS_ONLY = /^(在售|停售|缺货|active|inactive|out of stock|–|-)$/i;
  const asinFromBlob = (blob) => {
    const text = String(blob || '');
    const fromUrl = text.match(/(?:\\/dp\\/|\\/gp\\/product\\/|asin=|\\/product\\/)([A-Z0-9]{10})/i);
    if (fromUrl) return fromUrl[1].toUpperCase();
    const plain = text.match(/\\b([A-Z0-9]{10})\\b/);
    if (plain && /[0-9]/.test(plain[1])) return plain[1].toUpperCase();
    return '';
  };
  const collectRoots = (node, out = []) => {
    if (!node) return out;
    out.push(node);
    if (node.shadowRoot) collectRoots(node.shadowRoot, out);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) collectRoots(el.shadowRoot, out);
    });
    return out;
  };
  const roots = collectRoots(document);
  const rows = [];
  const seen = new Set();

  const pushRow = (asin, productName, extra = {}) => {
    if (!asin || seen.has(asin)) return;
    let name = String(productName || '').trim();
    if (!name || STATUS_ONLY.test(name)) name = asin;
    if (name.length < 3) return;
    seen.add(asin);
    rows.push({
      rank_no: rows.length + 1,
      product_name: name.slice(0, 180),
      asin,
      sku: extra.sku || '',
      revenue_30d: extra.revenue_30d || '',
      orders_30d: extra.orders_30d || '0',
      page_views: extra.page_views || '0',
      ad_spend_30d: extra.ad_spend_30d || '',
      acos: extra.acos || '',
      tacos: extra.tacos || '',
      conversion_rate: extra.conversion_rate || '',
      inventory: extra.inventory || '0',
      currency: 'USD',
    });
  };

  for (const root of roots) {
    for (const table of root.querySelectorAll('table')) {
      table.querySelectorAll('tbody tr, tr').forEach((tr) => {
        const tds = Array.from(tr.querySelectorAll('td, th'));
        if (!tds.length) return;
        let asin = '';
        let productName = '';
        tds.forEach((td) => {
          const cell = (td.innerText || '').trim();
          const href = td.querySelector('a')?.href || '';
          const found = asinFromBlob(`${href} ${cell}`);
          if (found) asin = found;
          if (!productName && cell.length > 6 && !STATUS_ONLY.test(cell) && !asinFromBlob(cell)) {
            productName = cell;
          }
          const link = td.querySelector('a');
          if (link) {
            const linked = (link.getAttribute('title') || link.innerText || '').trim();
            if (linked.length > productName.length && !STATUS_ONLY.test(linked)) {
              productName = linked;
            }
          }
        });
        if (asin) pushRow(asin, productName);
      });
    }
  }

  for (const root of roots) {
    for (const a of root.querySelectorAll('a[href]')) {
      const href = a.href || '';
      const asin = asinFromBlob(href);
      if (!asin) continue;
      const linked = (a.getAttribute('title') || a.innerText || '').trim();
      pushRow(asin, linked);
    }
  }

  return rows.slice(0, 50);
}
"""

EXTRACT_BR_GRID_JS = EXTRACT_PERFORMANCE_TABLE_JS

EXTRACT_BR_BODY_TEXT_JS = """
() => {
  const money = (raw) => {
    const match = String(raw || '').replace(/,/g, '').match(/(?:US?\\$|€|£|¥)?\\s*([\\d]+(?:\\.\\d+)?)/i);
    if (!match) return '';
    const num = parseFloat(match[1]);
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const integer = (raw) => {
    const match = String(raw || '').replace(/,/g, '').match(/(\\d+)/);
    return match ? match[1] : '0';
  };
  const UI_ACTION = /^(了解更多|创建\\s*A\\/?B\\s*试验|查看建议|编辑未来|learn more|create a\\/?b test)/i;
  const isAsinLine = (line) => /^[A-Z0-9]{10}$/.test(line) && /[0-9]/.test(line) && !/^G\\d{9}$/.test(line);
  const lines = (document.body.innerText || '').split(/\\n+/).map((s) => s.trim()).filter(Boolean);
  const rows = [];
  const seen = new Set();

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!isAsinLine(line)) continue;
    const asin = line.toUpperCase();
    if (seen.has(asin)) continue;
    let end = lines.length;
    for (let j = i + 1; j < lines.length; j += 1) {
      if (isAsinLine(lines[j])) {
        end = j;
        break;
      }
    }
    const windowLines = lines.slice(i + 1, Math.min(end, i + 16));
    let productName = '';
    const moneyVals = [];
    const intVals = [];
    windowLines.forEach((entry) => {
      if (isAsinLine(entry) || UI_ACTION.test(entry)) return;
      if (/GMT|UTC|AM|PM/i.test(entry) && /\\d{4}[/-]\\d{1,2}/.test(entry)) return;
      const revInline = entry.match(/US\\$\\s*([\\d,]+(?:\\.\\d+)?)/i);
      if (revInline) {
        const value = money(revInline[1]);
        if (value) moneyVals.push(value);
        return;
      }
      if (/US?\\$/.test(entry)) {
        const value = money(entry);
        if (value) moneyVals.push(value);
        return;
      }
      if (/^[\\d,]+(?:\\.\\d+)?\\s*%$/.test(entry)) return;
      const sessInline = entry.match(/(?:会话|session|page views?|浏览量)[^\\d]*([\\d,]+)/i);
      if (sessInline) {
        intVals.unshift(integer(sessInline[1]));
        return;
      }
      if (/^[\\d,]+$/.test(entry)) {
        const value = integer(entry);
        if (value !== '0') intVals.push(value);
        return;
      }
      if (!productName && entry.length > 12 && /[A-Za-z]/.test(entry) && !/^US?\\$/.test(entry)) {
        productName = entry;
      }
    });
    const revenue = moneyVals.length ? moneyVals[0] : '';
    const sessions = intVals.length ? intVals[0] : '0';
    const orders = intVals.length >= 2 ? intVals[1] : (intVals.length === 1 && !sessions ? intVals[0] : '0');
    if (!revenue && (!orders || orders === '0') && (!sessions || sessions === '0')) continue;
    seen.add(asin);
    rows.push({
      rank_no: rows.length + 1,
      product_name: (productName || asin).slice(0, 180),
      asin,
      sku: '',
      revenue_30d: revenue,
      orders_30d: orders || '0',
      page_views: sessions || '0',
      ad_spend_30d: '',
      acos: '',
      tacos: '',
      conversion_rate: '',
      inventory: '0',
      currency: 'USD',
    });
  }
  return rows.slice(0, 100);
}
"""


EXTRACT_ORDERS_JS = """
() => {
  const orderRe = /\\b(\\d{3}-\\d{7}-\\d{7})\\b/;
  const asinRe = /\\b([A-Z0-9]{10})\\b/gi;
  const moneyRe = /(?:US\\$|\\$|USD)\\s*([\\d,]+(?:\\.\\d+)?)/i;
  const qtyRe = /(?:Qty|数量|Quantity)[:\\s]*(\\d+)/i;
  const seen = new Set();
  const rows = [];

  const collectRoots = (node, out = []) => {
    if (!node) return out;
    out.push(node);
    if (node.shadowRoot) collectRoots(node.shadowRoot, out);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) collectRoots(el.shadowRoot, out);
    });
    return out;
  };

  const asinFromText = (text) => {
    const matches = [...String(text || '').matchAll(asinRe)];
    for (const match of matches) {
      const asin = String(match[1] || '').toUpperCase();
      if (/^G\\d{9}$/.test(asin)) continue;
      if (!/[0-9]/.test(asin)) continue;
      return asin;
    }
    return '';
  };

  const pushOrder = (payload) => {
    const orderNo = String(payload.order_no || '').trim();
    if (!orderNo || seen.has(orderNo)) return;
    seen.add(orderNo);
    rows.push({
      order_no: orderNo,
      asin: payload.asin || '',
      sku: payload.sku || '',
      product_name: String(payload.product_name || '').slice(0, 180),
      quantity: payload.quantity || 1,
      fulfillment_type: payload.fulfillment_type || 'fba',
      status: payload.status || 'pending',
      amount: payload.amount || '',
      currency: 'USD',
      ordered_at: payload.ordered_at || '',
      ship_deadline: payload.ship_deadline || '',
      buyer_region: payload.buyer_region || '',
    });
  };

  const parseRowText = (text) => {
    const body = String(text || '').trim();
    if (!body) return;
    const orderMatch = body.match(orderRe);
    if (!orderMatch) return;
    const lines = body.split('\\n').map((s) => s.trim()).filter(Boolean);
    const moneyMatch = body.match(moneyRe);
    const qtyMatch = body.match(qtyRe);
    let status = 'pending';
    if (/已取消|Canceled|Cancelled/i.test(body)) status = 'canceled';
    else if (/已发货|Shipped/i.test(body)) status = 'shipped';
    else if (/待揽收|Packed/i.test(body)) status = 'packed';
    const fulfillment = /自发货|MFN|Seller/i.test(body) ? 'fbm' : 'fba';
    const productName = lines.find((l) => l.length > 8 && !orderMatch[0].includes(l) && !asinRe.test(l)) || '';
    pushOrder({
      order_no: orderMatch[1],
      asin: asinFromText(body),
      product_name: productName,
      quantity: qtyMatch ? Number(qtyMatch[1]) : 1,
      fulfillment_type: fulfillment,
      status,
      amount: moneyMatch ? moneyMatch[1].replace(/,/g, '') : '',
    });
  };

  for (const root of collectRoots(document)) {
    root.querySelectorAll('table tbody tr, [role="row"], kat-table-row').forEach((tr) => {
      if (tr.querySelector?.('th,[role="columnheader"]')) return;
      parseRowText(tr.innerText || '');
    });
    root.querySelectorAll('[role="grid"] [role="row"], kat-table-body kat-table-row').forEach((row) => {
      if (row.querySelector?.('[role="columnheader"]')) return;
      parseRowText(row.innerText || '');
    });
  }

  if (!rows.length) {
    const chunks = (document.body.innerText || '').split(orderRe);
    for (let i = 1; i < chunks.length; i += 2) {
      const orderNo = chunks[i];
      const tail = chunks[i + 1] || '';
      parseRowText(`${orderNo}\\n${tail.slice(0, 500)}`);
    }
  }

  return rows.slice(0, 500);
}
"""


EXTRACT_DEEP_BODY_TEXT_JS = """
() => {
  const parts = [];
  const seen = new Set();
  const walk = (node) => {
    if (!node) return;
    const text = (node.innerText || '').trim();
    if (text && text.length > 2 && !seen.has(text)) {
      seen.add(text);
      parts.push(text);
    }
    if (node.shadowRoot) walk(node.shadowRoot);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) walk(el.shadowRoot);
    });
  };
  walk(document.body);
  return parts.join('\\n');
}
"""


EXTRACT_CASES_JS = """
() => {
  const rows = [];
  const seen = new Set();
  const pushCase = (payload) => {
    const id = String(payload.case_id || payload.id || '').trim();
    if (!id || seen.has(id)) return;
    seen.add(id);
    rows.push({
      id: payload.id || `case_${rows.length + 1}`,
      case_id: id,
      title: String(payload.title || 'Case').slice(0, 160),
      status: payload.status || 'pending',
      opened_at: payload.opened_at || '',
      note: String(payload.note || '').slice(0, 220),
    });
  };
  const text = document.body.innerText || '';
  const patterns = [
    [/管理(?:您的)?案例日志[^\\d]*(\\d+)/i, '管理案例日志待处理'],
    [/Manage\\s*your\\s*case\\s*log[^\\d]*(\\d+)/i, 'Case log pending'],
    [/Case\\s*log[^\\d]*(\\d+)/i, 'Case log pending'],
    [/(\\d+)\\s+cases?\\s+requiring/i, 'Cases requiring attention'],
    [/(\\d+)\\s+issues?\\s+requiring/i, 'Issues requiring attention'],
    [/问题日志[^\\d]*(\\d+)/i, '问题日志待处理'],
  ];
  patterns.forEach(([regex, title], index) => {
    const match = text.match(regex);
    if (match && Number(match[1]) > 0) {
      pushCase({
        id: `case_home_${index + 1}`,
        case_id: `home_case_${index + 1}`,
        title,
        status: 'pending',
        note: `页面显示 ${match[1]} 个问题需关注`,
      });
    }
  });
  document.querySelectorAll('table tbody tr, [role="row"]').forEach((tr, index) => {
    const line = (tr.innerText || '').trim();
    if (!line || line.length < 8) return;
    const caseMatch = line.match(/(?:Case|案例|Case ID|问题编号)[^\\d]*(\\d{6,})/i);
    if (!caseMatch) return;
    const caseId = caseMatch[1];
    const lines = line.split('\\n').map((s) => s.trim()).filter(Boolean);
    pushCase({
      id: `case_row_${caseId}`,
      case_id: caseId,
      title: lines[0] || `Case ${caseId}`,
      status: /closed|已关闭|resolved|已解决/i.test(line) ? 'closed' : 'pending',
      note: line.slice(0, 220),
    });
  });
  return rows.slice(0, 20);
}
"""


def parse_orders_from_text(text: str, *, default_status: str = "pending") -> list[dict[str, Any]]:
    body = text or ""
    order_re = re.compile(r"\b(\d{3}-\d{7}-\d{7})\b")
    money_re = re.compile(r"(?:US\$|\$|USD)\s*([\d,]+(?:\.\d+)?)", re.I)
    qty_re = re.compile(r"(?:Qty|数量|Quantity)[:\s]*(\d+)", re.I)
    asin_re = re.compile(r"\b([A-Z0-9]{10})\b", re.I)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in order_re.finditer(body):
        order_no = match.group(1)
        if order_no in seen:
            continue
        seen.add(order_no)
        start = max(0, match.start() - 120)
        end = min(len(body), match.end() + 420)
        chunk = body[start:end]
        status = default_status
        if re.search(r"已取消|Canceled|Cancelled", chunk, re.I):
            status = "canceled"
        elif re.search(r"已发货|Shipped", chunk, re.I):
            status = "shipped"
        money_match = money_re.search(chunk)
        qty_match = qty_re.search(chunk)
        asin_match = asin_re.search(chunk)
        asin = ""
        if asin_match:
            candidate = asin_match.group(1).upper()
            if re.search(r"[0-9]", candidate) and not re.match(r"^G\d{9}$", candidate):
                asin = candidate
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        product_name = next(
            (line for line in lines if len(line) > 8 and order_no not in line and not asin_re.fullmatch(line)),
            "",
        )
        rows.append(
            {
                "order_no": order_no,
                "asin": asin,
                "sku": "",
                "product_name": product_name[:180],
                "quantity": int(qty_match.group(1)) if qty_match else 1,
                "fulfillment_type": "fbm" if re.search(r"自发货|MFN|Seller", chunk, re.I) else "fba",
                "status": status,
                "amount": money_match.group(1).replace(",", "") if money_match else "",
                "currency": "USD",
                "ordered_at": "",
                "ship_deadline": "",
                "buyer_region": "",
            }
        )
    return rows[:500]


def parse_inventory_cards_from_text(text: str) -> list[dict[str, Any]]:
    body = text or ""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    asin_re = re.compile(r"^[A-Z0-9]{10}$", re.I)
    label_rules = [
        (re.compile(r"^(可售|available)$", re.I), "inventory"),
        (re.compile(r"^(在库|on hand|on-hand)$", re.I), "on_hand"),
        (re.compile(r"^(FBA\s*可售|available\s*\(fba\)|fulfillable)$", re.I), "inventory"),
        (re.compile(r"^(页面浏览量|page views?|sessions?)$", re.I), "page_views"),
        (re.compile(r"^(售出件数|units sold|ordered units|销量)$", re.I), "orders_30d"),
        (re.compile(r"^(销售额|sales)$", re.I), "revenue_30d"),
        (re.compile(r"^(可售数量|available quantity)$", re.I), "inventory_alt"),
    ]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    def money(raw: str) -> str:
        match = re.search(r"([\d,]+(?:\.\d+)?)", raw.replace(",", ""))
        return f"{float(match.group(1)):.2f}" if match else ""

    def integer(raw: str) -> str:
        match = re.search(r"(\d+)", raw.replace(",", ""))
        return match.group(1) if match else "0"

    for index, line in enumerate(lines):
        if not asin_re.match(line) or not re.search(r"[0-9]", line):
            continue
        asin = line.upper()
        if asin in seen:
            continue
        product_name = ""
        for back in range(max(0, index - 6), index):
            if len(lines[back]) > 18 and lines[back].upper() != "ASIN":
                product_name = lines[back]
        metrics: dict[str, str] = {}
        for j in range(index + 1, min(len(lines), index + 45)):
            if asin_re.match(lines[j]):
                break
            for pattern, key in label_rules:
                if not pattern.match(lines[j]):
                    continue
                nxt = lines[j + 1] if j + 1 < len(lines) else ""
                if nxt in {"--", "—"}:
                    continue
                if key == "revenue_30d":
                    value = money(nxt) or money(lines[j])
                    if value:
                        metrics[key] = value
                else:
                    metrics[key] = integer(nxt)
            rev_inline = re.search(r"US\$\s*([\d,]+(?:\.\d+)?)", lines[j], re.I)
            if rev_inline and "revenue_30d" not in metrics:
                metrics["revenue_30d"] = money(rev_inline.group(1))
        inventory = metrics.get("inventory") or metrics.get("inventory_alt") or metrics.get("on_hand") or "0"
        seen.add(asin)
        rows.append(
            {
                "rank_no": len(rows) + 1,
                "product_name": (product_name or asin)[:180],
                "asin": asin,
                "sku": "",
                "revenue_30d": metrics.get("revenue_30d", ""),
                "orders_30d": metrics.get("orders_30d", "0"),
                "page_views": metrics.get("page_views", "0"),
                "ad_spend_30d": "",
                "acos": "",
                "tacos": "",
                "conversion_rate": "",
                "inventory": inventory,
                "currency": "USD",
            }
        )
    return rows[:120]


EXTRACT_MESSAGES_JS = """
() => {
  const rows = [];
  const nodes = Array.from(document.querySelectorAll('table tbody tr, [data-testid*="message"], .message-row'));
  nodes.forEach((node, index) => {
    const text = (node.innerText || '').trim();
    if (!text || text.length < 8) return;
    const orderMatch = text.match(/\\b(\\d{3}-\\d{7}-\\d{7})\\b/);
    const lines = text.split('\\n').map(s => s.trim()).filter(Boolean);
    const buyerName = lines[0] || 'Buyer';
    const subject = lines.find(l => l.length > 5 && l !== buyerName) || '买家消息';
    rows.push({
      id: `msg_${index + 1}`,
      buyer_name: buyerName.slice(0, 80),
      order_no: orderMatch ? orderMatch[1] : '',
      subject: subject.slice(0, 120),
      preview: text.slice(0, 220),
      received_at: '',
      sla_hours: 24,
      status: 'pending',
    });
  });
  return rows.slice(0, 30);
}
"""


EXTRACT_REVIEWS_JS = """
() => {
  const rows = [];
  const orderRe = /\\b\\d{3}-\\d{7}-\\d{7}\\b/;
  const dateRe = /\\d{4}[\\/-]\\d{1,2}[\\/-]\\d{1,2}/;
  const tables = Array.from(document.querySelectorAll('table'));

  const pushRow = (date, rating, orderNo, content, index) => {
    if (!rating || rating > 3 || !orderNo) return;
    rows.push({
      id: `rev_${orderNo}_${rating}`,
      order_no: orderNo,
      asin: '',
      product_name: '',
      rating,
      content: (content || '').slice(0, 300),
      reviewed_at: date || '',
      status: 'pending',
    });
  };

  for (const table of tables) {
    const headerText = (table.innerText || '').slice(0, 400);
    if (!/(日期|Date)/i.test(headerText) || !/(评级|Rating)/i.test(headerText)) continue;
    if (!/(订单|Order)/i.test(headerText)) continue;

    const trs = table.querySelectorAll('tbody tr');
    trs.forEach((tr, index) => {
      const cells = Array.from(tr.querySelectorAll('td')).map((c) => (c.innerText || '').trim());
      if (cells.length >= 3) {
        const date = (cells[0].match(dateRe) || [])[0] || cells[0];
        const rating = parseInt(cells[1], 10);
        const orderNo = (cells[2].match(orderRe) || [])[0] || '';
        const content = cells.length > 3 ? cells.slice(3).join(' ').trim() : '';
        pushRow(date, rating, orderNo, content, index);
        return;
      }

      const text = (tr.innerText || '').trim();
      if (!text) return;
      const orderMatch = text.match(orderRe);
      if (!orderMatch) return;
      const lines = text.split('\\n').map((s) => s.trim()).filter(Boolean);
      let rating = 0;
      let date = '';
      for (const line of lines) {
        if (/^[1-5]$/.test(line)) rating = parseInt(line, 10);
        if (dateRe.test(line)) date = (line.match(dateRe) || [])[0];
      }
      const content = lines
        .filter((l) => l !== String(rating) && l !== date && !orderRe.test(l) && l !== '选择一个')
        .join(' ')
        .trim();
      pushRow(date, rating, orderMatch[0], content, index);
    });
    if (rows.length) break;
  }
  return rows.slice(0, 30);
}
"""


def parse_reviews_from_text(text: str) -> list[dict[str, Any]]:
    """从反馈管理器页面纯文本解析 1–3 星差评（兜底）。"""
    body = text or ""
    if "反馈管理器" not in body and "feedback manager" not in body.lower():
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    order_re = re.compile(r"\b(\d{3}-\d{7}-\d{7})\b")

    inline_re = re.compile(
        r"(\d{4}/\d{1,2}/\d{1,2})\s+([1-5])\s+(\d{3}-\d{7}-\d{7})",
    )
    for match in inline_re.finditer(body):
        date, rating_text, order_no = match.group(1), match.group(2), match.group(3)
        rating = int(rating_text)
        if rating > 3:
            continue
        dedupe = f"{order_no}:{rating}"
        if dedupe in seen:
            continue
        seen.add(dedupe)
        rows.append(
            {
                "id": f"rev_{order_no}_{rating}",
                "order_no": order_no,
                "asin": "",
                "product_name": "",
                "rating": rating,
                "content": "",
                "reviewed_at": date,
                "status": "pending",
            }
        )

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    skip_tokens = {"选择一个", "", "操作", "评论", "评级", "订单编号", "日期"}

    index = 0
    while index < len(lines):
        date_match = re.match(r"(\d{4}/\d{1,2}/\d{1,2})$", lines[index])
        if not date_match or index + 2 >= len(lines):
            index += 1
            continue

        rating_match = re.match(r"^([1-5])$", lines[index + 1])
        order_match = order_re.search(lines[index + 2])
        if not rating_match or not order_match:
            index += 1
            continue

        rating = int(rating_match.group(1))
        order_no = order_match.group(1)
        if rating <= 3:
            content_parts: list[str] = []
            cursor = index + 3
            while cursor < len(lines):
                part = lines[cursor]
                if re.match(r"\d{4}/\d{1,2}/\d{1,2}$", part):
                    break
                if part in skip_tokens or order_re.fullmatch(part) or re.match(r"^[1-5]$", part):
                    cursor += 1
                    continue
                content_parts.append(part)
                cursor += 1
                if len(" ".join(content_parts)) >= 300:
                    break

            dedupe = f"{order_no}:{rating}"
            if dedupe not in seen:
                seen.add(dedupe)
                rows.append(
                    {
                        "id": f"rev_{order_no}_{rating}",
                        "order_no": order_no,
                        "asin": "",
                        "product_name": "",
                        "rating": rating,
                        "content": " ".join(content_parts)[:300],
                        "reviewed_at": date_match.group(1),
                        "status": "pending",
                    }
                )
        index += 1

    return rows[:30]


EXTRACT_COUPONS_JS = """
() => {
  const rows = [];
  const tables = Array.from(document.querySelectorAll('table'));
  const dateRe = /\\d{4}[\\/-]\\d{1,2}[\\/-]\\d{1,2}/;
  for (const table of tables) {
    const header = (table.innerText || '').slice(0, 500);
    if (!/(促销|Promotion|Coupon|优惠券|折扣|Discount)/i.test(header)) continue;
    table.querySelectorAll('tbody tr').forEach((tr, index) => {
      const text = (tr.innerText || '').trim();
      if (!text || text.length < 6) return;
      const lines = text.split('\\n').map((s) => s.trim()).filter(Boolean);
      const name = lines[0] || `Coupon ${index + 1}`;
      const discount = (text.match(/(\\d+\\s*%|US\\$\\s*[\\d.]+|\\$\\s*[\\d.]+)/) || [])[0] || '';
      const dates = text.match(dateRe) || [];
      let status = 'active';
      if (/过期|Expired|ended/i.test(text)) status = 'expired';
      else if (/即将|Expiring|ending soon/i.test(text)) status = 'expiring';
      else if (/异常|Error|invalid/i.test(text)) status = 'abnormal';
      rows.push({
        id: `cpn_${index + 1}`,
        name: name.slice(0, 160),
        discount: discount || '',
        start_at: dates[0] || '',
        end_at: dates[1] || dates[0] || '',
        status,
        redemptions: 0,
        budget: 0,
        note: '',
      });
    });
    if (rows.length) break;
  }
  return rows.slice(0, 30);
}
"""


EXTRACT_SHIPMENTS_JS = """
() => {
  const rows = [];
  const shipmentRe = /\\b(FBA[A-Z0-9]{8,}|STAR-[A-Z0-9-]+)\\b/i;
  const intRe = /\\b(\\d{1,6})\\b/g;
  const tables = Array.from(document.querySelectorAll('table'));
  for (const table of tables) {
    const header = (table.innerText || '').slice(0, 500);
    if (!/(货件|Shipment|Inbound|入库|FBA)/i.test(header)) continue;
    table.querySelectorAll('tbody tr').forEach((tr, index) => {
      const text = (tr.innerText || '').trim();
      const shipMatch = text.match(shipmentRe);
      if (!shipMatch) return;
      const lines = text.split('\\n').map((s) => s.trim()).filter(Boolean);
      const nums = [...text.matchAll(intRe)].map((m) => Number(m[1]));
      const expected = nums.length >= 2 ? nums[nums.length - 2] : (nums[0] || 0);
      const received = nums.length >= 2 ? nums[nums.length - 1] : expected;
      let status = 'in_transit';
      if (/已送达|Delivered|Closed|已完成|Receiving complete/i.test(text)) status = 'delivered';
      else if (/缺件|Shortage|Missing/i.test(text) || (expected > 0 && received < expected)) status = 'shortage';
      else if (/无货|no inventory|closed without/i.test(text)) status = 'closed_no_stock';
      const alertLevel = status === 'shortage' || status === 'closed_no_stock' ? 'danger' : 'normal';
      rows.push({
        id: `shp_${shipMatch[1]}`,
        shipment_id: shipMatch[1],
        product_name: lines.find((l) => l.length > 4 && !shipmentRe.test(l)) || '',
        sku: '',
        units_expected: expected,
        units_received: received,
        destination: '',
        status,
        alert_level: alertLevel,
        expected_at: '',
        note: '',
      });
    });
    if (rows.length) break;
  }
  return rows.slice(0, 40);
}
"""


EXTRACT_ADS_SUMMARY_JS = """
() => {
  const money = (raw) => {
    const match = String(raw || '').match(/([\\d,]+(?:\\.\\d+)?)/);
    if (!match) return '';
    const num = parseFloat(match[1].replace(/,/g, ''));
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const text = document.body.innerText || '';
  const spend = text.match(/(?:Spend|花费|支出|Cost)[\\s\\S]{0,80}?US\\$\\s*([\\d,]+(?:\\.\\d+)?)/i)
    || text.match(/US\\$\\s*([\\d,]+(?:\\.\\d+)?)[\\s\\S]{0,40}?(?:Spend|花费)/i);
  const sales = text.match(/(?:Ad sales|广告销售额|Sales attributed)[\\s\\S]{0,80}?US\\$\\s*([\\d,]+(?:\\.\\d+)?)/i);
  const acos = text.match(/ACOS[\\s\\S]{0,40}?([\\d.]+)\\s*%/i)
    || text.match(/([\\d.]+)\\s*%[\\s\\S]{0,20}?ACOS/i);
  return {
    ad_spend_30d: spend ? money(spend[1]) : '',
    ad_sales_30d: sales ? money(sales[1]) : '',
    acos: acos ? acos[1] : '',
  };
}
"""

EXTRACT_AD_CAMPAIGNS_JS = """
() => {
  const money = (value) => {
    const match = String(value || '').match(/([\\d,]+(?:\\.\\d+)?)/);
    if (!match) return '';
    const num = parseFloat(match[1].replace(/,/g, ''));
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const percent = (value) => {
    const match = String(value || '').match(/([\\d.]+)\\s*%/);
    return match ? match[1] : '';
  };
  const asinRe = /\\b([A-Z0-9]{10})\\b/gi;
  const rows = [];
  const seen = new Set();

  const collectRoots = (node, out = []) => {
    if (!node) return out;
    out.push(node);
    if (node.shadowRoot) collectRoots(node.shadowRoot, out);
    node.querySelectorAll?.('*').forEach((el) => {
      if (el.shadowRoot) collectRoots(el.shadowRoot, out);
    });
    return out;
  };

  const asinFromText = (text) => {
    const matches = [...String(text || '').matchAll(asinRe)];
    for (const match of matches) {
      const asin = String(match[1] || '').toUpperCase();
      if (/^G\\d{9}$/.test(asin)) continue;
      if (!/[0-9]/.test(asin)) continue;
      return asin;
    }
    return '';
  };

  const pushCampaign = (payload) => {
    const key = payload.asin || payload.campaign_name;
    if (!key || seen.has(key)) return;
    if (!payload.ad_spend_30d && !payload.acos) return;
    seen.add(key);
    rows.push({
      campaign_name: String(payload.campaign_name || '').slice(0, 160),
      asin: payload.asin || '',
      sku: payload.sku || '',
      ad_spend_30d: payload.ad_spend_30d || '',
      ad_sales_30d: payload.ad_sales_30d || '',
      acos: payload.acos || '',
    });
  };

  const rules = [
    { key: 'name', pattern: /(campaign|广告活动|name|活动名称)/i },
    { key: 'asin', pattern: /asin/i },
    { key: 'sku', pattern: /sku/i },
    { key: 'spend', pattern: /(spend|花费|cost|支出)/i },
    { key: 'sales', pattern: /(sales|销售额|revenue|广告销售额)/i },
    { key: 'acos', pattern: /acos/i },
  ];

  const parseTable = (table) => {
    const headerCells = Array.from(
      table.querySelectorAll('thead th, tr th, tr:first-child td, [role="columnheader"]')
    );
    const headers = headerCells.map((c) => (c.innerText || '').trim()).filter(Boolean);
    if (!headers.length) return;
    const headerText = headers.join(' ');
    if (!/(campaign|广告|spend|花费|acos|cost|活动)/i.test(headerText)) return;
    const columnMap = {};
    headers.forEach((label, index) => {
      for (const rule of rules) {
        if (rule.pattern.test(label) && columnMap[rule.key] == null) {
          columnMap[rule.key] = index;
          break;
        }
      }
    });
    table.querySelectorAll('tbody tr, [role="row"]').forEach((tr) => {
      if (tr.querySelector('th,[role="columnheader"]')) return;
      const cells = Array.from(tr.querySelectorAll('td, [role="gridcell"]')).map((td) => (td.innerText || '').trim());
      if (!cells.length) return;
      const text = cells.join('\\n');
      const spend = columnMap.spend != null ? money(cells[columnMap.spend]) : '';
      const acos = columnMap.acos != null ? percent(cells[columnMap.acos]) : '';
      const name = columnMap.name != null ? cells[columnMap.name] : cells[0];
      pushCampaign({
        campaign_name: name,
        asin: columnMap.asin != null ? asinFromText(cells[columnMap.asin]) : asinFromText(text),
        sku: columnMap.sku != null ? cells[columnMap.sku].slice(0, 80) : '',
        ad_spend_30d: spend,
        ad_sales_30d: columnMap.sales != null ? money(cells[columnMap.sales]) : '',
        acos,
      });
    });
  };

  for (const root of collectRoots(document)) {
    root.querySelectorAll('table, [role="grid"], kat-table').forEach(parseTable);
  }

  if (!rows.length) {
    const text = document.body.innerText || '';
    const lines = text.split('\\n').map((s) => s.trim()).filter(Boolean);
    lines.forEach((line, index) => {
      if (!/(campaign|广告|sp|sb|sd)/i.test(line)) return;
      const spend = money(line);
      const acos = percent(line);
      if (!spend && !acos) return;
      pushCampaign({
        campaign_name: line.slice(0, 160),
        asin: asinFromText(lines.slice(index, index + 4).join(' ')),
        ad_spend_30d: spend,
        acos,
      });
    });
  }

  return rows.slice(0, 120);
}
"""

EXTRACT_AD_SKU_SPEND_JS = """
() => {
  const money = (value) => {
    const match = String(value || '').match(/([\\d,]+(?:\\.\\d+)?)/);
    if (!match) return '';
    const num = parseFloat(match[1].replace(/,/g, ''));
    return Number.isFinite(num) ? num.toFixed(2) : '';
  };
  const percent = (value) => {
    const match = String(value || '').match(/([\\d.]+)\\s*%/);
    return match ? match[1] : '';
  };
  const asinRe = /\\b([A-Z0-9]{10})\\b/g;
  const text = document.body.innerText || '';
  const lines = text.split('\\n').map((s) => s.trim()).filter(Boolean);
  const rows = [];
  const seen = new Set();
  for (let i = 0; i < lines.length; i += 1) {
    const asinMatch = lines[i].match(asinRe);
    if (!asinMatch) continue;
    const asin = asinMatch[1].toUpperCase();
    if (seen.has(asin)) continue;
    const windowText = lines.slice(Math.max(0, i - 1), i + 6).join(' ');
    const spendMatch = windowText.match(/(?:US\\$|\\$)\\s*([\\d,]+(?:\\.\\d+)?)/);
    const acosMatch = windowText.match(/([\\d.]+)\\s*%/);
    const spend = spendMatch ? money(spendMatch[1]) : '';
    const acos = acosMatch ? percent(acosMatch[0]) : '';
    if (!spend && !acos) continue;
    seen.add(asin);
    rows.push({
      campaign_name: lines[i].slice(0, 160),
      asin,
      sku: '',
      ad_spend_30d: spend,
      ad_sales_30d: '',
      acos,
    });
  }
  return rows.slice(0, 80);
}
"""


def parse_coupons_from_text(text: str) -> list[dict[str, Any]]:
    body = text or ""
    if (
        "促销" not in body
        and "Promotion" not in body
        and "Coupon" not in body
        and "优惠券" not in body
        and "coupon" not in body.lower()
    ):
        return []
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(body.splitlines()):
        line = line.strip()
        if not line or len(line) < 4:
            continue
        discount = re.search(r"(\d+\s*%|US\$\s*[\d.]+|\$\s*[\d.]+)", line)
        if not discount:
            continue
        rows.append(
            {
                "id": f"cpn_txt_{index}",
                "name": line[:160],
                "discount": discount.group(1),
                "start_at": "",
                "end_at": "",
                "status": "expired" if "过期" in line or "Expired" in line else "active",
                "redemptions": 0,
                "budget": 0,
                "note": "",
            }
        )
    return rows[:30]


def parse_shipments_from_text(text: str) -> list[dict[str, Any]]:
    body = text or ""
    if not body.strip():
        return []
    if not re.search(r"(货件|Shipment|Inbound|入库|FBA|shipping\s*queue)", body, re.I):
        return []
    rows: list[dict[str, Any]] = []
    shipment_re = re.compile(r"\b(FBA[A-Z0-9]{8,}|STAR-[A-Z0-9-]+)\b", re.I)
    for match in shipment_re.finditer(body):
        sid = match.group(1)
        snippet = body[match.start() : match.start() + 200]
        nums = [int(n) for n in re.findall(r"\b(\d{1,6})\b", snippet)]
        expected = nums[-2] if len(nums) >= 2 else (nums[0] if nums else 0)
        received = nums[-1] if len(nums) >= 2 else expected
        status = "shortage" if expected > 0 and received < expected else "in_transit"
        if "已送达" in snippet or "Delivered" in snippet:
            status = "delivered"
        rows.append(
            {
                "id": f"shp_{sid}",
                "shipment_id": sid,
                "product_name": "",
                "sku": "",
                "units_expected": expected,
                "units_received": received,
                "destination": "",
                "status": status,
                "alert_level": "danger" if status == "shortage" else "normal",
                "expected_at": "",
                "note": "",
            }
        )
    dedup: dict[str, dict[str, Any]] = {}
    for row in rows:
        dedup[row["shipment_id"]] = row
    return list(dedup.values())[:40]


def parse_seller_news_from_text(text: str) -> list[dict[str, Any]]:
    body = text or ""
    items: list[dict[str, Any]] = []
    if "卖家新闻" not in body and "Seller news" not in body.lower():
        return items

    block_match = re.search(
        r"卖家新闻\s*(.*?)(?=全局快照|商品绩效|建议|隐藏式|$)",
        body,
        re.S,
    )
    block = block_match.group(1) if block_match else body
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    skip = {"查看全部", "卖家新闻", "Seller news"}
    index = 0
    while index < len(lines):
        title = lines[index]
        if title in skip or re.match(r"^\d+$", title) or re.match(r"^\d+月", title):
            index += 1
            continue
        if len(title) < 8:
            index += 1
            continue
        date = ""
        if index + 1 < len(lines) and re.search(r"\d+月\s*\d+", lines[index + 1]):
            date = lines[index + 1]
        items.append(
            {
                "id": f"news_{len(items) + 1}",
                "title": title[:180],
                "summary": title[:220],
                "published_at": date,
                "status": "unread",
            }
        )
        index += 1
        if len(items) >= 10:
            break

    if not items and "业绩通知" in body:
        items.append(
            {
                "id": "news_perf",
                "title": "业绩通知",
                "summary": "请查看卖家平台业绩通知",
                "published_at": "",
                "status": "unread",
            }
        )
    return items


def parse_cases_from_text(text: str) -> list[dict[str, Any]]:
    body = text or ""
    cases: list[dict[str, Any]] = []
    patterns = [
        (r"管理(?:您的)?案例日志[^\n]*?(\d+)", "管理案例日志待处理"),
        (r"管理问题日志[^\n]*?(\d+)", "管理问题日志待处理"),
        (r"Manage\s*your\s*case\s*log[^\n]*?(\d+)", "Case log pending"),
        (r"Case\s*log[^\n]*?(\d+)", "Case log pending"),
        (r"(\d+)\s+cases?\s+requiring", "Cases requiring attention"),
        (r"(\d+)\s+issues?\s+requiring", "Issues requiring attention"),
        (r"(\d+)\s+open\s+cases?", "Open cases"),
        (r"问题日志[^\n]*?(\d+)", "问题日志待处理"),
        (r"待处理问题[^\n]*?(\d+)", "待处理问题"),
        (r"(\d+)\s*个?待处理(?:案例|问题)", "待处理案例"),
    ]
    for index, (pattern, title) in enumerate(patterns):
        match = re.search(pattern, body, re.I)
        if match and int(match.group(1)) > 0:
            cases.append(
                {
                    "id": f"case_home_{index + 1}",
                    "case_id": f"home_case_{index + 1}",
                    "title": title,
                    "status": "pending",
                    "opened_at": "",
                    "note": f"首页显示 {match.group(1)} 个问题需关注",
                }
            )
            break
    news_match = re.search(r"(?:业绩通知|Performance notifications)[^\n]*?(\d+)", body, re.I)
    if news_match:
        count = int(news_match.group(1))
        if count > 0:
            cases.append(
                {
                    "id": "news_home_1",
                    "case_id": "performance_notifications",
                    "title": "业绩通知",
                    "status": "pending",
                    "opened_at": "",
                    "note": f"近 120 天有 {count} 条业绩通知",
                }
            )
    if not any(item.get("case_id") == "performance_notifications" for item in cases):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            if not re.search(r"业绩通知|performance notifications", line, re.I):
                continue
            for offset in range(1, 4):
                if index + offset >= len(lines):
                    break
                digit = re.match(r"^(\d+)$", lines[index + offset])
                if digit and int(digit.group(1)) > 0:
                    cases.append(
                        {
                            "id": "news_home_multiline",
                            "case_id": "performance_notifications",
                            "title": "业绩通知",
                            "status": "pending",
                            "opened_at": "",
                            "note": f"首页显示 {digit.group(1)} 条业绩通知",
                        }
                    )
                    break
            if cases:
                break
    return cases
