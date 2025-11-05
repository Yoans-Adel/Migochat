"""
Business Services Module
=========================
Business logic and domain-specific services.

This module provides:
- Facebook Lead Center integration (lead management, scoring, classification)
- Keyword Manager (fuzzy matching, Arabic text normalization)
- Message Source Tracker (campaign attribution, source tracking)

Implements core business rules and lead management workflows.
"""

from typing import TYPE_CHECKING

# Lazy imports for better performance
if TYPE_CHECKING:
    from .facebook_lead_center_service import FacebookLeadCenterService
    from .keyword_manager import KeywordManager
    from .message_source_tracker import MessageSourceTracker

__all__ = [
    "FacebookLeadCenterService",
    "KeywordManager",
    "MessageSourceTracker",
]


def __getattr__(name: str):
    """Lazy import mechanism for better performance."""
    if name == "FacebookLeadCenterService":
        from .facebook_lead_center_service import FacebookLeadCenterService
        return FacebookLeadCenterService

    if name == "KeywordManager":
        from .keyword_manager import KeywordManager
        return KeywordManager

    if name == "MessageSourceTracker":
        from .message_source_tracker import MessageSourceTracker
        return MessageSourceTracker

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
