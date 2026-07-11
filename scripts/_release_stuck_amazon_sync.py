"""将卡住的 Amazon sync/agent 任务标记为 failed，解除 409 锁。"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend/data/crosshub.db"

MSG = "手动解除：任务长时间无结果，已作废以便重新同步"


def main() -> None:
    conn = sqlite3.connect(DB)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        """
        SELECT j.id, j.agent_task_id
        FROM amazon_sync_job j
        WHERE j.status IN ('pending', 'running')
        ORDER BY j.created_at DESC
        """
    ).fetchall()
    if not rows:
        print("no stuck jobs")
        return
    for job_id, task_id in rows:
        conn.execute(
            "UPDATE agent_task SET status='failed', error_message=?, updated_at=? WHERE id=? AND status IN ('pending','running')",
            (MSG, now, task_id),
        )
        conn.execute(
            "UPDATE amazon_sync_job SET status='failed', error_message=?, updated_at=? WHERE id=? AND status IN ('pending','running')",
            (MSG, now, job_id),
        )
        print("released:", job_id, task_id)
    conn.commit()


if __name__ == "__main__":
    main()
