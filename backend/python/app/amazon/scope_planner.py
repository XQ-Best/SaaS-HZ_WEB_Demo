"""按 sync scope 生成页面任务列表。"""
from __future__ import annotations

from app.amazon.page_registry import SCOPE_TASK_KEYS, resolve_task, PageTask


def normalize_scope(scope: str) -> str:
    value = (scope or "account_health").strip().lower()
    if value == "insights":
        return "reports"
    return value


def plan_tasks(scope: str) -> list[PageTask]:
    normalized = normalize_scope(scope)
    keys = SCOPE_TASK_KEYS.get(normalized, SCOPE_TASK_KEYS["account_health"])
    tasks: list[PageTask] = []
    for key in keys:
        task = resolve_task(key)
        if task is not None:
            tasks.append(task)
    return tasks
