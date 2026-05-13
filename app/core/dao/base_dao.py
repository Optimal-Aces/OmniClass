import uuid
from datetime import datetime
from app.core.dao.database import Database

class BaseDAO:
    table = ""

    def __init__(self):
        self.db = Database()

    @property
    def conn(self):
        return self.db.connect()

    def new_id(self) -> str:
        return str(uuid.uuid4())

    def now(self) -> str:
        return datetime.utcnow().isoformat()

    def get_by_id(self, record_id: str):
        return self.conn.execute(
            f"SELECT * FROM {self.table} WHERE id = ?", (record_id,)
        ).fetchone()

    def delete(self, record_id: str):
        self.conn.execute(
            f"DELETE FROM {self.table} WHERE id = ?", (record_id,)
        )
        self.conn.commit()