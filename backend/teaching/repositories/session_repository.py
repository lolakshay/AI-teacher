"""
Session Repository Interface and In-Memory Implementation conforming to Section 6.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from backend.teaching.schemas.session import TeachingSessionState

class SessionRepository(ABC):
    @abstractmethod
    def create_session(self, session: TeachingSessionState) -> TeachingSessionState:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[TeachingSessionState]:
        pass

    @abstractmethod
    def save_session(self, session: TeachingSessionState) -> TeachingSessionState:
        pass

    @abstractmethod
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[TeachingSessionState]:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        pass

class InMemorySessionRepository(SessionRepository):
    def __init__(self):
        self._sessions: Dict[str, TeachingSessionState] = {}

    def create_session(self, session: TeachingSessionState) -> TeachingSessionState:
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[TeachingSessionState]:
        return self._sessions.get(session_id)

    def save_session(self, session: TeachingSessionState) -> TeachingSessionState:
        self._sessions[session.session_id] = session
        return session

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[TeachingSessionState]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        updated_data = session.model_dump()
        updated_data.update(updates)
        new_session = TeachingSessionState(**updated_data)
        self._sessions[session_id] = new_session
        return new_session

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

# Global instance
session_repository = InMemorySessionRepository()
