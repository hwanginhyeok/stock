"""Storage test fixtures — in-memory SQLite database."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.database import Base


@pytest.fixture
def db_session(monkeypatch: pytest.MonkeyPatch):
    """In-memory SQLite session with all tables created.

    Patches get_session and get_engine so that repositories use the
    test database.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    from contextlib import contextmanager

    @contextmanager
    def _mock_get_session():
        session = TestSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Patch in storage modules
    monkeypatch.setattr("src.core.database.get_session", _mock_get_session)
    monkeypatch.setattr("src.core.database.get_engine", lambda: engine)
    monkeypatch.setattr("src.core.database.get_session_factory", lambda: TestSession)

    # Clear lru_cache for engine/session factory
    try:
        from src.core.database import get_engine, get_session_factory
        get_engine.cache_clear()
        get_session_factory.cache_clear()
    except Exception:
        pass

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()
