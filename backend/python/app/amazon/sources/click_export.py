"""Playwright 点击导出 CSV 按钮（仅限报表主区域，禁止误点页脚「下载 App」）。"""
from __future__ import annotations

from app.amazon.navigation_guard import assert_allowed_url, click_header_scoped, click_scoped

# BR 页 kat-button 常用 label="下载" / "Download"（无 csv 后缀）
_DOWNLOAD_BTN_RE = (
    r"^(download|下载|export|导出)$|"
    r"download\s*(report|csv|spreadsheet)?|"
    r"export\s*(csv|report|all|全部)?|"
    r"导出\s*(csv|报表|报告|全部)?|"
    r"下载\s*(csv|报表|报告)?"
)
_CSV_MENU_RE = r"csv|comma.?separated|\.csv|逗号|电子表格"

_SHADOW_EXPORT_JS = """
() => {
  const blocked = (node) => {
    const footer = document.querySelector('footer, [class*="footer"]');
    return footer && footer.contains(node);
  };
  const tryClick = (node) => {
    if (!node || blocked(node)) return false;
    const text = (node.innerText || node.getAttribute('label') || node.getAttribute('aria-label') || '').trim();
    if (/^(export|导出|download|下载)$/i.test(text)) {
      node.click();
      return true;
    }
    return false;
  };
  const walk = (root) => {
    if (!root) return false;
    for (const node of root.querySelectorAll('a, button, kat-button, kat-link, span, [role="button"]')) {
      if (tryClick(node)) return true;
    }
    for (const node of root.querySelectorAll('*')) {
      if (node.shadowRoot && walk(node.shadowRoot)) return true;
    }
    return false;
  };
  return walk(document.body);
}
"""

_INVENTORY_TOOLBAR_EXPORT_JS = """
() => {
  const blocked = (node) => {
    if (!node) return true;
    const footer = document.querySelector('footer, [class*="footer"], [id*="footer"]');
    if (footer && footer.contains(node)) return true;
    const href = (node.getAttribute?.('href') || node.href || '').toLowerCase();
    if (/sellermobileapp|mobileapp/i.test(href)) return true;
    return false;
  };
  const labelOf = (node) =>
  (node.innerText || node.getAttribute('label') || node.getAttribute('aria-label') || node.value || '').trim();
  const isExport = (node) => /^export$/i.test(labelOf(node));
  const scopes = [
    ...document.querySelectorAll(
      '[class*="toolbar"], [class*="Toolbar"], kat-toolbar, [data-testid*="toolbar"], header, #sc-content-container, kat-workflow, main, [role="main"]'
    ),
    document.body,
  ];
  const walk = (root) => {
    if (!root) return false;
    for (const node of root.querySelectorAll(
      'button, kat-button, kat-dropdown-button, kat-link, a, [role="button"], input[type="button"]'
    )) {
      if (!blocked(node) && isExport(node)) {
        node.click();
        return true;
      }
    }
    for (const node of root.querySelectorAll('*')) {
      if (node.shadowRoot && walk(node.shadowRoot)) return true;
    }
    return false;
  };
  for (const scope of scopes) {
    if (walk(scope)) return true;
  }
  return false;
}
"""


def _click_export_candidates(page) -> bool:
    if click_scoped(
        page,
        _DOWNLOAD_BTN_RE,
        kinds="button, kat-button, kat-dropdown-button, kat-link, a, [role='button'], input[type='button']",
    ):
        return True
    if click_header_scoped(
        page,
        _DOWNLOAD_BTN_RE,
        kinds="a, button, kat-button, kat-link, [role='button'], span",
    ):
        return True
    return bool(page.evaluate(_SHADOW_EXPORT_JS))


def click_download_csv(page) -> None:
    assert_allowed_url(page.url, context="before_br_download")
    if not _click_export_candidates(page):
        raise RuntimeError("未在报表主区域找到 CSV 导出按钮（已排除页脚）")
    page.wait_for_timeout(1200)
    click_scoped(
        page,
        _CSV_MENU_RE,
        kinds="kat-menu-item, kat-option, [role='menuitem'], button, kat-button, li, a, span",
    )
    assert_allowed_url(page.url, context="after_br_download_click")


def click_inventory_export(page) -> None:
    """库存页 Export（含 shadow DOM / 顶栏工具栏）。"""
    clicked = False
    try:
        page.get_by_role("button", name="Export", exact=True).first.click(timeout=5000)
        clicked = True
    except Exception:
        try:
            page.get_by_role("button", name="导出", exact=True).first.click(timeout=3000)
            clicked = True
        except Exception:
            pass
    if not clicked:
        clicked = bool(page.evaluate(_INVENTORY_TOOLBAR_EXPORT_JS))
    if not clicked and not _click_export_candidates(page):
        raise RuntimeError("未找到库存 Export/导出 按钮")
    page.wait_for_timeout(1500)
    if not click_scoped(
        page,
        _CSV_MENU_RE + r"|all\s*listings|全部|inventory|库存|listing",
        kinds="kat-menu-item, kat-option, [role='menuitem'], button, kat-button, li, a, span, label",
    ):
        page.evaluate(
            """
            () => {
              const re = /csv|comma|all listings|全部|inventory report/i;
              const blocked = (node) => {
                const footer = document.querySelector('footer, [class*="footer"]');
                return footer && footer.contains(node);
              };
              const walk = (root) => {
                if (!root) return false;
                for (const node of root.querySelectorAll('button, kat-button, kat-option, kat-menu-item, a, li, span, label')) {
                  if (blocked(node)) continue;
                  const text = (node.innerText || node.getAttribute('label') || '').trim();
                  if (re.test(text)) { node.click(); return true; }
                }
                for (const node of root.querySelectorAll('*')) {
                  if (node.shadowRoot && walk(node.shadowRoot)) return true;
                }
                return false;
              };
              return walk(document.body);
            }
            """
        )


