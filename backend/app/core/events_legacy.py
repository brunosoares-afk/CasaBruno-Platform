from datetime import datetime
import json

from database.database import db
from app.core.logger.logger import logger


class EventBus:

    def publish(self, event, source="system", data=None):

        if data is None:
            data = {}

        item = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "source": source,
            "data": data
        }

        db.execute(
            """
            INSERT INTO events
            (
                timestamp,
                event,
                source,
                data
            )
            VALUES
            (
                ?,?,?,?
            )
            """,
            (
                item["timestamp"],
                item["event"],
                item["source"],
                json.dumps(item["data"])
            )
        )

        logger.info(
            source,
            f"EVENT -> {event}"
        )

        return item

    def emit(self, event, source="system", data=None):

        return self.publish(
            event,
            source,
            data
        )

    def latest(self, limit=20):

        return self.history(limit)

    def history(self, limit=100):

        rows = db.fetchall(
            """
            SELECT
                timestamp,
                event,
                source,
                data
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        for row in rows:

            try:
                row["data"] = json.loads(row["data"])
            except:
                row["data"] = {}

        return rows


eventbus = EventBus()
