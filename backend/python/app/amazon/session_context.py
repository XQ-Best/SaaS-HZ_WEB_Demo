"""紫鸟 CDP 会话上下文（登录检测、截图、merchantId）。"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

CAPTURE_DIR = Path(__file__).resolve().parents[3] / "data" / "amazon-captures"


class AmazonLoginRequiredError(RuntimeError):
    def __init__(self, message: str, *, capture_path: str = "") -> None:
        super().__init__(message)
        self.capture_path = capture_path


def extract_debug_port(start_result: dict[str, Any]) -> int:
    for key in ("debuggingPort", "debugPort", "debugging_port", "cdpPort", "port"):
        value = start_result.get(key)
        if value is not None and str(value).strip().isdigit():
            return int(str(value).strip())
    browser = start_result.get("browser")
    if isinstance(browser, dict):
        for key in ("debuggingPort", "debugPort", "debugging_port", "cdpPort", "port"):
            value = browser.get(key)
            if value is not None and str(value).strip().isdigit():
                return int(str(value).strip())
    raise RuntimeError(f"startBrowser 未返回 debuggingPort: {start_result!r}")


def save_capture(page, *, store_name: str, suffix: str) -> str:
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]+", "_", store_name or "amazon")[:40]
    path = CAPTURE_DIR / f"{safe_name}_{suffix}_{int(time.time())}.png"
    page.screenshot(path=str(path), full_page=True)
    return str(path)


def looks_logged_in(body_text: str, url: str) -> bool:
    body = body_text or ""
    lowered = body.lower()
    if "/home" in (url or "") and ("全局快照" in body or "global snapshot" in lowered):
        return True
    if "账户状况" in body or "account health" in lowered:
        return True
    if "seller central" in lowered or "卖家平台" in body:
        return "sign in" not in lowered and "sign-in" not in lowered
    return False


def looks_login_page(body_text: str, url: str) -> bool:
    body = body_text or ""
    lowered = body.lower()
    if "sign in" in lowered or "sign-in" in lowered:
        return "seller central" not in lowered and "卖家平台" not in body
    if "登录" in body and "账户状况" not in body and "全局快照" not in body:
        return True
    if "/ap/signin" in (url or "").lower():
        return True
    return False


def require_seller_logged_in(page, body_text: str, *, store_name: str = "") -> None:
    if looks_login_page(body_text, page.url):
        capture = save_capture(page, store_name=store_name, suffix="login")
        raise AmazonLoginRequiredError(
            f"Amazon 卖家后台未登录，截图: {capture}",
            capture_path=capture,
        )
    if not looks_logged_in(body_text, page.url):
        capture = save_capture(page, store_name=store_name, suffix="login")
        raise AmazonLoginRequiredError(
            f"Amazon 卖家后台会话无效，请在紫鸟中重新登录 Seller Central。截图: {capture}",
            capture_path=capture,
        )


def goto(page, url: str, wait_ms: int = 10000) -> str:
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(wait_ms)
    return page.inner_text("body")


def resolve_merchant_id(page) -> str:
    try:
        merchant_id = page.evaluate(
            """
            () => {
              const fromUrl = new URL(location.href).searchParams.get('merchantId')
                || new URL(location.href).searchParams.get('merchantid');
              if (fromUrl) return fromUrl;
              const html = document.documentElement.innerHTML || '';
              const patterns = [
                /merchantId["':=\\s]+(A[A-Z0-9]{9,14})/i,
                /"merchantId":"(A[A-Z0-9]{9,14})"/i,
                /merchant_id["':=\\s]+(A[A-Z0-9]{9,14})/i,
              ];
              for (const pattern of patterns) {
                const match = html.match(pattern);
                if (match) return match[1];
              }
              return '';
            }
            """
        )
        return str(merchant_id or "").strip()
    except Exception:
        return ""


class SessionContext:
    def __init__(self, page, *, store_name: str = "", merchant_id: str = "") -> None:
        self.page = page
        self.store_name = store_name
        self.merchant_id = merchant_id

    def screenshot(self, suffix: str) -> str:
        return save_capture(self.page, store_name=self.store_name, suffix=suffix)

    def body_text(self) -> str:
        return self.page.inner_text("body")

    def ensure_merchant_id(self) -> str:
        if self.merchant_id:
            return self.merchant_id
        self.merchant_id = resolve_merchant_id(self.page)
        return self.merchant_id
