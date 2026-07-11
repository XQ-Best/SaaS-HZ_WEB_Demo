"""orders-v3 分页爬取。"""

from __future__ import annotations

from typing import Any

from app.amazon.page_urls import ORDER_LIST_SPECS

from app.amazon.parsers.seller_pages import EXTRACT_ORDERS_JS, parse_orders_from_text

from app.amazon.session_context import looks_login_page



_ORDER_SCROLL_JS = """

async () => {

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  for (let i = 0; i < 8; i += 1) {

    window.scrollBy(0, 1200);

    await sleep(250);

  }

}

"""





def crawl_orders_v3(page, *, max_pages: int = 15) -> list[dict[str, Any]]:

    all_orders: list[dict[str, Any]] = []

    seen_keys: set[str] = set()



    def ingest(batch: list[dict[str, Any]], default_status: str, url: str) -> None:

        for row in batch:

            if not isinstance(row, dict):

                continue

            order_no = str(row.get("order_no") or "").strip()

            if not order_no or order_no in seen_keys:

                continue

            seen_keys.add(order_no)

            if not row.get("status") or row.get("status") == "pending":

                row["status"] = default_status

            if "/fba/" in url:

                row["fulfillment_type"] = "fba"

            elif "/mfn/" in url:

                row["fulfillment_type"] = "fbm"

            all_orders.append(row)



    for spec in ORDER_LIST_SPECS:

        url = spec["url"]

        default_status = spec["status"]

        try:

            page.goto(url, wait_until="domcontentloaded")

            page.wait_for_timeout(9000)

            try:

                page.wait_for_load_state("networkidle", timeout=15000)

            except Exception:

                pass

            body = page.inner_text("body")

            if looks_login_page(body, page.url):

                continue

            page.evaluate(_ORDER_SCROLL_JS)

            page.wait_for_timeout(1500)

            for page_index in range(max_pages):

                batch = page.evaluate(EXTRACT_ORDERS_JS) or []

                if not isinstance(batch, list):

                    batch = []

                if not batch and page_index == 0:

                    batch = parse_orders_from_text(body, default_status=default_status)

                ingest(batch, default_status, url)

                clicked = page.evaluate(

                    """

                    () => {

                      const btn = [...document.querySelectorAll('button, a, kat-pagination button')].find((el) =>

                        /next|下一页|›|→|>>/i.test((el.innerText || el.getAttribute('aria-label') || '').trim())

                      );

                      if (!btn || btn.disabled || btn.getAttribute('aria-disabled') === 'true') return false;

                      btn.click();

                      return true;

                    }

                    """

                )

                if not clicked:

                    break

                page.wait_for_timeout(4000)

                page.evaluate(_ORDER_SCROLL_JS)

                page.wait_for_timeout(1200)

                body = page.inner_text("body")

                fallback = parse_orders_from_text(body, default_status=default_status)

                ingest(fallback, default_status, url)

        except Exception:

            continue

    return all_orders

