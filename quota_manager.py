import time
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


class QuotaManager:
    """
    Manages API request quotas with per-user and global rate limiting.

    Features:
    - Hourly and daily request limits per user
    - Global quota tracking
    - Persistent quota storage using JSON
    - Exponential backoff for rate limiting
    """

    def __init__(
        self,
        max_requests_per_hour=10,
        max_requests_per_day=50,
        global_max_daily=1000,
        quota_file="quota_data.json"
    ):
        self.max_per_hour = max_requests_per_hour
        self.max_per_day = max_requests_per_day
        self.global_max_daily = global_max_daily
        self.quota_file = Path(quota_file)
        self.request_history = defaultdict(list)
        self._load_quota_data()

    def _load_quota_data(self):
        """Load quota data from persistent storage."""
        if self.quota_file.exists():
            try:
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                    for user_id, timestamps in data.items():
                        self.request_history[user_id] = [
                            datetime.fromisoformat(ts) for ts in timestamps
                        ]
            except (json.JSONDecodeError, IOError):
                self.request_history = defaultdict(list)

    def _save_quota_data(self):
        """Persist quota data to storage."""
        try:
            data = {
                user_id: [ts.isoformat() for ts in timestamps]
                for user_id, timestamps in self.request_history.items()
            }
            with open(self.quota_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save quota data: {e}")

    def _prune_old_requests(self, user_id):
        """Remove requests older than 24 hours."""
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        self.request_history[user_id] = [
            ts for ts in self.request_history[user_id]
            if ts > cutoff
        ]

    def get_user_quota_status(self, user_id):
        """Get current quota status for a user."""
        self._prune_old_requests(user_id)
        now = datetime.now()
        user_requests = self.request_history[user_id]

        hourly_requests = len([
            t for t in user_requests
            if t > (now - timedelta(hours=1))
        ])
        daily_requests = len(user_requests)

        return {
            "hourly_used": hourly_requests,
            "hourly_limit": self.max_per_hour,
            "hourly_remaining": max(0, self.max_per_hour - hourly_requests),
            "daily_used": daily_requests,
            "daily_limit": self.max_per_day,
            "daily_remaining": max(0, self.max_per_day - daily_requests),
            "hourly_reset_in_minutes": self._minutes_until_reset(user_requests, timedelta(hours=1)),
            "daily_reset_in_hours": self._minutes_until_reset(user_requests, timedelta(days=1)) / 60,
        }

    def _minutes_until_reset(self, requests, window):
        """Calculate minutes until quota window resets."""
        if not requests:
            return 0
        oldest_in_window = min(
            (datetime.now() - ts).total_seconds() / 60
            for ts in requests
            if datetime.now() - ts < window
        )
        minutes_in_window = window.total_seconds() / 60
        return max(0, minutes_in_window - oldest_in_window)

    def can_make_request(self, user_id):
        """
        Check if user can make an API request.
        Returns (allowed, reason_if_denied, wait_seconds)
        """
        self._prune_old_requests(user_id)
        now = datetime.now()
        user_requests = self.request_history[user_id]

        daily_requests = len(user_requests)
        if daily_requests >= self.max_per_day:
            reset_time = user_requests[0] + timedelta(days=1)
            wait_seconds = max(0, int((reset_time - now).total_seconds()))
            return (
                False,
                f"Daily quota exceeded ({self.max_per_day} requests/day). "
                f"Resets in {wait_seconds // 3600}h {(wait_seconds % 3600) // 60}m",
                wait_seconds
            )

        recent_hour = [t for t in user_requests if t > (now - timedelta(hours=1))]
        if len(recent_hour) >= self.max_per_hour:
            reset_time = recent_hour[0] + timedelta(hours=1)
            wait_seconds = max(0, int((reset_time - now).total_seconds()))
            return (
                False,
                f"Hourly quota exceeded ({self.max_per_hour} requests/hour). "
                f"Retry in {wait_seconds} seconds",
                wait_seconds
            )

        global_daily = self._get_global_daily_count()
        if global_daily >= self.global_max_daily:
            return (
                False,
                "Global quota exceeded. Service temporarily unavailable. Please try later.",
                3600
            )

        return (True, None, 0)

    def _get_global_daily_count(self):
        """Get total requests across all users in the current day."""
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        total = sum(
            len([ts for ts in requests if ts > cutoff])
            for requests in self.request_history.values()
        )
        return total

    def record_request(self, user_id):
        """Record a successful API request."""
        self.request_history[user_id].append(datetime.now())
        self._save_quota_data()

    def get_global_quota_status(self):
        """Get global quota status across all users."""
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        total_requests = sum(
            len([ts for ts in requests if ts > cutoff])
            for requests in self.request_history.values()
        )

        return {
            "global_used": total_requests,
            "global_limit": self.global_max_daily,
            "global_remaining": max(0, self.global_max_daily - total_requests),
            "total_users": len(self.request_history),
        }
