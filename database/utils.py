"""
Database Utility Functions
Helper functions for working with database models and enums
"""
from typing import Any, Union
from enum import Enum


def enum_to_value(enum_obj: Union[Enum, Any, None], default: Any = None) -> Any:
    """
    Safely convert an enum to its value.

    This is a type-safe replacement for getattr(enum, 'value', None)
    that provides better IDE support and type checking.

    Args:
        enum_obj: The enum object to convert (can be None)
        default: Default value to return if enum_obj is None

    Returns:
        The enum's value if enum_obj is not None, otherwise default

    Examples:
        >>> from database.enums import LeadStage
        >>> stage = LeadStage.INTAKE
        >>> enum_to_value(stage)
        'Intake'
        >>> enum_to_value(None, "unknown")
        'unknown'
    """
    if enum_obj is None:
        return default

    if not isinstance(enum_obj, Enum):
        # If it's already a value (string/int), return it
        return enum_obj

    return enum_obj.value


def enum_to_name(enum_obj: Union[Enum, Any, None], default: str = "") -> str:
    """
    Safely get the name of an enum.

    Args:
        enum_obj: The enum object (can be None)
        default: Default value to return if enum_obj is None

    Returns:
        The enum's name if enum_obj is not None, otherwise default

    Examples:
        >>> from database.enums import LeadStage
        >>> stage = LeadStage.INTAKE
        >>> enum_to_name(stage)
        'INTAKE'
    """
    if enum_obj is None:
        return default

    if not isinstance(enum_obj, Enum):
        return str(enum_obj)

    return enum_obj.name


def safe_enum_comparison(enum_obj: Union[Enum, Any, None], value: Any) -> bool:
    """
    Safely compare an enum to a value.

    Args:
        enum_obj: The enum object to compare (can be None)
        value: The value to compare against

    Returns:
        True if the enum's value equals the given value, False otherwise

    Examples:
        >>> from database.enums import LeadStage
        >>> stage = LeadStage.INTAKE
        >>> safe_enum_comparison(stage, 'Intake')
        True
        >>> safe_enum_comparison(None, 'Intake')
        False
    """
    if enum_obj is None:
        return False

    if isinstance(enum_obj, Enum):
        return enum_obj.value == value

    return enum_obj == value
