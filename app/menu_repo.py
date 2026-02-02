import json
from app.db import SessionLocal, MenuItem


def get_menu_as_list() -> list[dict]:
    db = SessionLocal()
    try:
        rows = db.query(MenuItem).order_by(MenuItem.name.asc()).all()
        return [
            {
                "item_id": r.item_id,
                "name": r.name,
                "aliases": json.loads(r.aliases_json),
            }
            for r in rows
        ]
    finally:
        db.close()
