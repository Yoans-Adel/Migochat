"""Helper functions for user update operations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from database import CustomerLabel, CustomerType, Governorate, LeadActivity, LeadStage, User


def enum_to_value(enum_val: Any) -> Optional[str]:
    """Convert enum to string value."""
    return enum_val.value if enum_val else None


def update_enum_field(
    user: User,
    field_name: str,
    new_value_str: str,
    enum_class: Any,
    error_message: str
) -> Tuple[bool, Optional[Tuple[str, Optional[str], str]]]:
    """Update an enum field and track changes.

    Args:
        user: User object to update
        field_name: Name of the field to update
        new_value_str: New value as string
        enum_class: Enum class (Governorate, LeadStage, etc.)
        error_message: Error message if invalid value

    Returns:
        Tuple of (success, change_record or None)

    Raises:
        HTTPException: If enum value is invalid
    """
    try:
        old_value = enum_to_value(getattr(user, field_name))
        setattr(user, field_name, enum_class(new_value_str))

        if field_name == 'lead_stage':
            setattr(user, 'last_stage_change', datetime.now(timezone.utc))

        if old_value != new_value_str:
            return True, (field_name, old_value, new_value_str)
        return True, None

    except ValueError:
        raise HTTPException(status_code=400, detail=error_message)


def update_user_fields(
    user: User,
    update_data: Dict[str, Any]
) -> List[Tuple[str, Optional[str], str]]:
    """Update user fields and track changes.

    Args:
        user: User object to update
        update_data: Dictionary of fields to update

    Returns:
        List of changes (field_name, old_value, new_value)
    """
    changes: List[Tuple[str, Optional[str], str]] = []

    if "first_name" in update_data:
        user.first_name = update_data["first_name"]

    if "last_name" in update_data:
        user.last_name = update_data["last_name"]

    if "governorate" in update_data:
        _, change = update_enum_field(
            user, 'governorate', update_data["governorate"],
            Governorate, "Invalid governorate"
        )
        if change:
            changes.append(change)

    if "lead_stage" in update_data:
        _, change = update_enum_field(
            user, 'lead_stage', update_data["lead_stage"],
            LeadStage, "Invalid lead stage"
        )
        if change:
            changes.append(change)

    if "customer_type" in update_data:
        _, change = update_enum_field(
            user, 'customer_type', update_data["customer_type"],
            CustomerType, "Invalid customer type"
        )
        if change:
            changes.append(change)

    if "customer_label" in update_data:
        _, change = update_enum_field(
            user, 'customer_label', update_data["customer_label"],
            CustomerLabel, "Invalid customer label"
        )
        if change:
            changes.append(change)

    return changes


def log_lead_activities(
    user: User,
    changes: List[Tuple[str, Optional[str], str]],
    db: Any
) -> None:
    """Log changes to lead activities table.

    Args:
        user: User object
        changes: List of changes to log
        db: Database session
    """
    for activity_type, old_val, new_val in changes:
        activity = LeadActivity(
            user_id=user.id,
            activity_type=f"{activity_type}_change",
            old_value=old_val,
            new_value=new_val,
            reason="Manual update from dashboard",
            automated=False,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(activity)
