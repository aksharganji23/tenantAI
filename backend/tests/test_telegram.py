from datetime import datetime, timedelta
from types import SimpleNamespace

import telegram_bot


class FakeQuery:
    def __init__(self, session):
        self.session = session

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.session


class FakeDb:
    def __init__(self, session):
        self.session = session
        self.deleted = False
        self.commits = 0

    def query(self, *_args):
        return FakeQuery(self.session)

    def delete(self, session):
        self.deleted = session

    def commit(self):
        self.commits += 1


def test_telegram_session_refreshes_after_activity(monkeypatch):
    current = datetime(2026, 1, 1, 12, 0, 0)
    session = SimpleNamespace(
        last_activity_at=current - timedelta(seconds=30),
        expires_at=current - timedelta(seconds=1),
    )
    db = FakeDb(session)
    monkeypatch.setattr(telegram_bot, "now", lambda: current)
    monkeypatch.setattr(telegram_bot.settings, "TELEGRAM_SESSION_TIMEOUT_SECONDS", 120)

    result = telegram_bot.get_session(123, db)

    assert result is session
    assert session.last_activity_at == current
    assert session.expires_at == current + timedelta(seconds=120)
    assert not db.deleted


def test_telegram_session_expires_after_inactivity(monkeypatch):
    current = datetime(2026, 1, 1, 12, 0, 0)
    session = SimpleNamespace(
        last_activity_at=current - timedelta(seconds=120),
        expires_at=current + timedelta(seconds=30),
    )
    db = FakeDb(session)
    monkeypatch.setattr(telegram_bot, "now", lambda: current)
    monkeypatch.setattr(telegram_bot.settings, "TELEGRAM_SESSION_TIMEOUT_SECONDS", 120)

    result = telegram_bot.get_session(123, db)

    assert result is None
    assert db.deleted is session
    assert db.commits == 1
