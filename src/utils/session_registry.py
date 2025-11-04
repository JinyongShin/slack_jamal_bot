"""Thread-safe file-based session registry for multi-agent debate."""

import json
import fcntl
from pathlib import Path
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# 프로젝트 루트의 공유 세션 파일 (하드코딩)
SHARED_SESSION_FILE = "./shared_sessions.json"


class FileSessionRegistry:
    """Thread-safe file-based session registry."""

    def __init__(self, file_path: str = SHARED_SESSION_FILE):
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Initialize file if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.write_text('{}')
            logger.info(f"Created session registry file: {self.file_path}")

    def get_session_id(self, thread_ts: str) -> Optional[str]:
        """
        Get session_id for a given thread.

        Args:
            thread_ts: Slack thread timestamp

        Returns:
            session_id if exists, None otherwise
        """
        try:
            with open(self.file_path, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    session_id = data.get(thread_ts)
                    if session_id:
                        logger.debug(f"Retrieved session for thread {thread_ts}: {session_id}")
                    return session_id
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Error reading session registry: {e}")
            return None

    def set_session_id(self, thread_ts: str, session_id: str):
        """
        Store session_id for a given thread.

        Args:
            thread_ts: Slack thread timestamp
            session_id: ADK session ID
        """
        try:
            with open(self.file_path, 'r+') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    data = json.load(f)
                    data[thread_ts] = session_id
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
                    logger.info(f"Stored session for thread {thread_ts}: {session_id}")
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Error writing session registry: {e}")
