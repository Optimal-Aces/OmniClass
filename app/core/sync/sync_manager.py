import threading
import logging
import time
from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self, db):
        self.db = db
        self._running = False

    def start(self):
        if not (SUPABASE_URL and SUPABASE_KEY):
            logger.warning("Supabase not configured — running offline only")
            return
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()
        logger.info("Sync manager started")

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                self._push_pending()
                self._pull_remote()
            except Exception as e:
                logger.error(f"Sync error: {e}")
            time.sleep(30)

    def _push_pending(self):
        conn = self.db.connect()
        rows = conn.execute(
            "SELECT * FROM sync_queue WHERE attempts < 3 ORDER BY created_at"
        ).fetchall()
        for row in rows:
            conn.execute(
                "UPDATE sync_queue SET attempts = attempts + 1 WHERE id = ?",
                (row["id"],)
            )
        conn.commit()

    def _pull_remote(self):
        pass