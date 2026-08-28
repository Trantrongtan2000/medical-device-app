"""Safety defaults for tests using canonical SQLite database."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import pytest
CANONICAL_DB = Path(__file__).resolve().parents[1] / "database" / "devices.db"
ALLOW_CANONICAL_MUTATIONS = os.getenv("HTM_ALLOW_CANONICAL_DB_TESTS") == "1"
UNSAFE_NODE_IDS = {
    "tests/test_needle_agent.py::test_two_phase_mutation_workflow",
    "tests/test_needle_agent.py::test_api_agent_mutation_confirm_flow",
    "tests/test_needle_agent.py::test_api_agent_mutation_cancel_flow",
    "tests/test_adversarial_safety.py::test_stale_state_rejection_on_concurrent_modification",
}
UNSAFE_MODULES = {"tests/test_transfers_api.py", "tests/test_transfers_transaction.py", "tests/test_repairs_api.py", "tests/test_documents_pdf.py"}
def _digest_db() -> tuple[int, str]:
    stat = CANONICAL_DB.stat()
    return stat.st_size, hashlib.sha256(CANONICAL_DB.read_bytes()).hexdigest()
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if ALLOW_CANONICAL_MUTATIONS: return
    skip = pytest.mark.skip(reason="canonical DB mutation test skipped; isolate DB before explicit opt-in")
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if nodeid in UNSAFE_NODE_IDS or nodeid.rsplit("::", 1)[0] in UNSAFE_MODULES: item.add_marker(skip)
@pytest.fixture(scope="session", autouse=True)
def canonical_db_unchanged() -> None:
    if not CANONICAL_DB.exists(): pytest.skip(f"canonical database not found: {CANONICAL_DB}")
    before = _digest_db()
    yield
    after = _digest_db()
    if after != before: pytest.fail(f"canonical database changed; isolate DB before tests: {CANONICAL_DB}")