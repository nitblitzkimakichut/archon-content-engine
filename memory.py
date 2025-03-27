from typing import Dict, Any, List
import sqlite3
import json
from datetime import datetime, timedelta
import os

class ContentMemory:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.db_path = "content_memory.db"
        self._initialize_database()

    def _initialize_database(self):
        """Create the database and tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE,
                    platform TEXT,
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_content(self, video_id: str, platform: str, analysis_data: Dict[str, Any]):
        """Add or update content analysis data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO content_memory 
                (video_id, platform, analysis_data, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (video_id, platform, json.dumps(analysis_data)))
            conn.commit()

    def get_content(self, video_id: str) -> Dict[str, Any]:
        """Retrieve content analysis data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT analysis_data FROM content_memory 
                WHERE video_id = ? AND 
                last_updated > datetime('now', '-? days')
            ''', (video_id, self.config.retention_days))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None

    def cleanup_old_entries(self):
        """Remove entries older than retention period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM content_memory 
                WHERE last_updated < datetime('now', '-? days')
            ''', (self.config.retention_days,))
            conn.commit()

    def backup_database(self):
        """Create a backup of the database"""
        backup_path = os.path.join(
            self.config.backup_location,
            f"content_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        os.system(f'cp {self.db_path} {backup_path}')