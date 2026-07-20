#!/usr/bin/env python3
from __future__ import annotations

import json

from app.amazon.page_urls import HOME_URL, INVENTORY_URLS
from app.amazon.session_context import extract_debug_port, require_seller_logged_in, save_capture
from app.ziniao.client import ZiniaoClient, ZiniaoConfig
from playwright.sync_api import sync_playwright

ziniao = ZiniaoClient(ZiniaoConfig.from_env())
ziniao.ensure_webdriver_client(wait_seconds=20)
start = ziniao.start_browser(browser_id="16505337258263", headless=False)
port = extract_debug_port(start)
try:
    with sync_playwright() as p:
        page = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}").contexts[0].pages[0]
        page.goto(HOME_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        require_seller_logged_in(page, page.inner_text("body"), store_name="YOTO")
        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(12000)
        cap = save_capture(page, store_name="YOTO", suffix="inv_export_find")
        print("capture", cap, flush=True)
        print("frames", len(page.frames), flush=True)
        for i, frame in enumerate(page.frames):
            try:
                txt = frame.inner_text("body")[:200].replace("\n", " | ")
                has = "Export" in frame.inner_text("body") or "导出" in frame.inner_text("body")
                print(f"frame[{i}] url={frame.url[:100]} export={has} text={txt[:120]}", flush=True)
            except Exception as exc:
                print(f"frame[{i}] err", exc, flush=True)
        body = page.inner_text("body")
        print("has Export", "Export" in body, "导出" in body, flush=True)
        for sel in [
            "text=Export",
            "text=导出",
            'a:has-text("Export")',
            'button:has-text("Export")',
            '[data-testid*="export"]',
        ]:
            try:
                print(sel, page.locator(sel).count(), flush=True)
            except Exception as exc:
                print(sel, "err", exc, flush=True)
        data = page.evaluate(
            """
            () => {
              const hits = [];
              const walk = (root) => {
                if (!root) return;
                const nodes = root.querySelectorAll ? [...root.querySelectorAll('*')] : [];
                for (const el of nodes) {
                  const t = (el.innerText || '').trim();
                  if (/^export$/i.test(t) || t === '导出') {
                    hits.push({
                      tag: el.tagName,
                      text: t,
                      id: el.id,
                      cls: String(el.className || '').slice(0, 80),
                    });
                  }
                  if (el.shadowRoot) walk(el.shadowRoot);
                }
              };
              walk(document.body);
              return hits.slice(0, 20);
            }
            """
        )
        print(json.dumps(data, ensure_ascii=False, indent=2), flush=True)
finally:
    ziniao.stop_browser(browser_id="16505337258263")
