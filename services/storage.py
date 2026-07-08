"""SQLite 存档 - 测算记录增删查"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "records.db"


def _conn():
    _DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            template_id TEXT NOT NULL,
            params TEXT NOT NULL,
            results TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_record(name: str, template_id: str, params: dict, results: dict = None) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO records (name, template_id, params, results, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (name, template_id, json.dumps(params, ensure_ascii=False), json.dumps(results, ensure_ascii=False) if results else None, now, now),
        )
        c.commit()
        return cur.lastrowid


def update_record(rid: int, name: str = None, params: dict = None, results: dict = None) -> bool:
    now = datetime.now().isoformat(timespec="seconds")
    sets, args = [], []
    if name is not None:
        sets.append("name=?"); args.append(name)
    if params is not None:
        sets.append("params=?"); args.append(json.dumps(params, ensure_ascii=False))
    if results is not None:
        sets.append("results=?"); args.append(json.dumps(results, ensure_ascii=False))
    sets.append("updated_at=?"); args.append(now)
    args.append(rid)
    with _conn() as c:
        c.execute(f"UPDATE records SET {','.join(sets)} WHERE id=?", args)
        c.commit()
        return c.rowcount > 0


def list_records(template_id: str = None) -> list[dict]:
    with _conn() as c:
        if template_id:
            rows = c.execute("SELECT * FROM records WHERE template_id=? ORDER BY updated_at DESC", (template_id,))
        else:
            rows = c.execute("SELECT * FROM records ORDER BY updated_at DESC")
        return [dict(r) for r in rows]


def get_record(rid: int) -> dict | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM records WHERE id=?", (rid,)).fetchone()
        return dict(r) if r else None


def delete_record(rid: int) -> bool:
    with _conn() as c:
        cur = c.execute("DELETE FROM records WHERE id=?", (rid,))
        c.commit()
        return cur.rowcount > 0
