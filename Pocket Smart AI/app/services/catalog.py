import json

from ..database import get_db


def history(user_id):
    with get_db() as db:
        rows = db.execute(
            """
            SELECT id, planner, input_json, result_json, created_at
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

    records = []

    for row in rows:
        records.append({
            "id": row["id"],
            "type": row["planner"],
            "data": json.loads(row["result_json"]),
            "created_at": row["created_at"]
        })

    return records


def one(user_id, recommendation_id):
    with get_db() as db:
        row = db.execute(
            """
            SELECT id, planner, input_json, result_json, created_at
            FROM recommendations
            WHERE id = ? AND user_id = ?
            """,
            (recommendation_id, user_id)
        ).fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "type": row["planner"],
        "data": json.loads(row["result_json"]),
        "created_at": row["created_at"]
    }