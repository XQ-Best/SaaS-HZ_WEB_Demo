"""Amazon 爬取分页面诊断。"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PageDiagnostic:
    key: str
    url: str
    ok: bool
    rows: int = 0
    duration_ms: int = 0
    warning: str = ""
    capture_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CrawlDiagnostics:
    pages: list[PageDiagnostic] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add(self, diagnostic: PageDiagnostic) -> None:
        self.pages.append(diagnostic)
        if diagnostic.warning and diagnostic.warning not in self.warnings:
            self.warnings.append(diagnostic.warning)

    def summary(self) -> dict[str, Any]:
        ok_count = sum(1 for item in self.pages if item.ok)
        failed = [item for item in self.pages if not item.ok]
        return {
            "pages_ok": ok_count,
            "pages_failed": len(failed),
            "warnings": list(self.warnings),
            "page_diagnostics": [item.to_dict() for item in self.pages],
        }
