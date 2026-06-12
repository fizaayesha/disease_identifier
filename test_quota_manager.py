import pytest
import os
from datetime import datetime, timedelta
from quota_manager import QuotaManager


@pytest.fixture
def quota_manager_instance(tmp_path):
    """Create a fresh QuotaManager instance for testing."""
    quota_file = tmp_path / "test_quota.json"
    return QuotaManager(
        max_requests_per_hour=3,
        max_requests_per_day=10,
        global_max_daily=50,
        quota_file=str(quota_file)
    )


def test_initial_quota_available(quota_manager_instance):
    """Test that quota is available for new user."""
    user_id = "test_user_1"
    can_request, reason, wait = quota_manager_instance.can_make_request(user_id)
    assert can_request is True
    assert reason is None
    assert wait == 0


def test_hourly_quota_exceeded(quota_manager_instance):
    """Test that hourly quota is enforced."""
    user_id = "test_user_2"
    manager = quota_manager_instance

    for _ in range(manager.max_per_hour):
        manager.record_request(user_id)

    can_request, reason, wait = manager.can_make_request(user_id)
    assert can_request is False
    assert "Hourly quota exceeded" in reason


def test_daily_quota_exceeded(quota_manager_instance):
    """Test that daily quota is enforced."""
    user_id = "test_user_3"
    manager = quota_manager_instance

    for _ in range(manager.max_per_day):
        manager.record_request(user_id)

    can_request, reason, wait = manager.can_make_request(user_id)
    assert can_request is False
    assert "Daily quota exceeded" in reason


def test_quota_status_tracking(quota_manager_instance):
    """Test quota status tracking."""
    user_id = "test_user_4"
    manager = quota_manager_instance

    manager.record_request(user_id)
    manager.record_request(user_id)

    status = manager.get_user_quota_status(user_id)
    assert status["hourly_used"] == 2
    assert status["hourly_remaining"] == manager.max_per_hour - 2
    assert status["daily_used"] == 2
    assert status["daily_remaining"] == manager.max_per_day - 2


def test_global_quota_status(quota_manager_instance):
    """Test global quota status."""
    manager = quota_manager_instance

    manager.record_request("user1")
    manager.record_request("user2")
    manager.record_request("user3")

    status = manager.get_global_quota_status()
    assert status["global_used"] == 3
    assert status["total_users"] == 3
    assert status["global_remaining"] == manager.global_max_daily - 3


def test_quota_persistence(tmp_path):
    """Test that quota data persists across instances."""
    quota_file = tmp_path / "persistent_quota.json"

    manager1 = QuotaManager(
        max_requests_per_hour=10,
        max_requests_per_day=100,
        quota_file=str(quota_file)
    )
    manager1.record_request("user_persist")
    manager1.record_request("user_persist")

    manager2 = QuotaManager(
        max_requests_per_hour=10,
        max_requests_per_day=100,
        quota_file=str(quota_file)
    )

    status = manager2.get_user_quota_status("user_persist")
    assert status["hourly_used"] == 2
    assert status["daily_used"] == 2


def test_quota_reset_after_window(quota_manager_instance):
    """Test that old requests are pruned."""
    user_id = "test_user_reset"
    manager = quota_manager_instance

    manager.record_request(user_id)
    initial_count = len(manager.request_history[user_id])
    assert initial_count == 1

    manager._prune_old_requests(user_id)
    assert len(manager.request_history[user_id]) == 1
