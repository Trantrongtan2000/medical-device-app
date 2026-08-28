from datetime import datetime, timedelta, timezone
import sqlite3

from app.needle_agent import MutationDraftManager


def _draft(**kwargs):
    return MutationDraftManager.create_draft(
        action_type=kwargs.get("action_type", "CREATE_WORK_ORDER"),
        device_id=1,
        asset_tag="BVQ7-TTB-00001",
        initial_state=kwargs.get("initial_state", {"status": "IN_SERVICE"}),
        state_version=1,
        proposed_payload={"issue_description": "test"},
        owner_user_id=kwargs.get("owner_user_id"),
    )


def test_execute_rejects_expired_draft_without_db_access(tmp_path):
    draft = _draft()
    draft.expires_at = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    ok, message, _ = MutationDraftManager.execute_draft(draft.draft_id, str(tmp_path / "missing.db"))
    assert not ok
    assert draft.status == "EXPIRED"
    assert "hết hạn" in message


def test_execute_rejects_wrong_owner_without_db_access(tmp_path):
    draft = _draft(owner_user_id="USR-1")
    ok, message, _ = MutationDraftManager.execute_draft(
        draft.draft_id, str(tmp_path / "missing.db"), actor_user_id="USR-2"
    )
    assert not ok
    assert draft.status == "PENDING_CONFIRMATION"
    assert "người dùng khác" in message


def test_work_order_rechecks_captured_status(tmp_path):
    db_path = tmp_path / "isolated.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE devices (id INTEGER PRIMARY KEY, facility_id INTEGER, status TEXT)")
        db.execute("CREATE TABLE maintenance_logs (device_id INTEGER, maintenance_type TEXT, maintenance_date TEXT, performed_by TEXT, description TEXT)")
        db.execute("INSERT INTO devices VALUES (1, 2, 'REPAIR')")
        db.commit()
    draft = _draft(initial_state={"status": "IN_SERVICE"})
    ok, message, _ = MutationDraftManager.execute_draft(draft.draft_id, str(db_path))
    assert not ok
    assert draft.status == "STALE_REJECTED"
    assert "thay đổi" in message

def test_execute_rejects_replay_after_claimed_execution(tmp_path):
    draft = _draft()
    draft.status = "EXECUTED"
    ok, message, _ = MutationDraftManager.execute_draft(draft.draft_id, str(tmp_path / "missing.db"))
    assert not ok
    assert "EXECUTED" in message