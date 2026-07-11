"""Fail orphaned Amazon sync after agent restart."""
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
task_id = "agt_7a37e139-96f6-4efa-8b93-9abf615ee7e8"
job_id = "amz_sync_5ae096f7-922e-49dc-a715-4b7d2022425b"
c = sqlite3.connect(DB)
c.execute(
    """
    UPDATE agent_task
    SET status='failed', error_code='CRAWL_INTERRUPTED', error_message='Agent restarted during sync',
        finished_at=?
    WHERE id=? AND status IN ('pending','running')
    """,
    (now, task_id),
)
c.execute(
    """
    UPDATE amazon_sync_job
    SET status='failed', error_code='CRAWL_INTERRUPTED', error_message='Agent restarted during sync',
        finished_at=?
    WHERE id=? AND status IN ('pending','running')
    """,
    (now, job_id),
)
c.commit()
print("updated", c.total_changes)
