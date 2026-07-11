import json
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "backend/data/crosshub.db"
for task_id in ("agt_db60c3b6-5669-420e-98b1-78ac82c07024", "agt_7aaac502-0cf5-4ffd-9bfb-a2bdc67cc939"):
    row = sqlite3.connect(db).execute(
        "SELECT status, result_json FROM agent_task WHERE id=?",
        (task_id,),
    ).fetchone()
    if not row or not row[1]:
        continue
    d = json.loads(row[1])
    print("===", task_id, row[0], "===")
    for x in d.get("page_diagnostics") or []:
        if isinstance(x, dict):
            print(x.get("key"), x.get("ok"), x.get("rows"), x.get("warning"), (x.get("url") or "")[:70])
    print("cases", len(d.get("cases") or []), "inv>0", sum(1 for p in d.get("products") or [] if int(p.get("inventory") or 0) > 0))
    print("pv>0", sum(1 for p in d.get("products") or [] if int(p.get("page_views") or 0) > 0))
