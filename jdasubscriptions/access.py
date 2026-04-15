# jdasubscriptions/access.py
# Canonical public interface for publication access control.
# Import from here in all views — not from services.access_services directly.

from jdasubscriptions.services.access_services import (
    user_can_access_publication,
    user_has_active_subscription,
    get_upgrade_recommendation,
)

__all__ = [
    "user_can_access_publication",
    "user_has_active_subscription",
    "get_upgrade_recommendation",
]
