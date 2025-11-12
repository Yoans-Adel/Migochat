"""
Tests for database utility functions
"""
import pytest
from database.utils import enum_to_value, enum_to_name, safe_enum_comparison
from database.enums import LeadStage, MessageSource, CustomerType


class TestEnumToValue:
    """Test enum_to_value function"""

    def test_enum_to_value_with_valid_enum(self):
        """Test converting valid enum to value"""
        stage = LeadStage.INTAKE
        result = enum_to_value(stage)
        assert result == "Intake"

    def test_enum_to_value_with_none(self):
        """Test converting None returns default"""
        result = enum_to_value(None)
        assert result is None

    def test_enum_to_value_with_none_and_default(self):
        """Test converting None with custom default"""
        result = enum_to_value(None, "unknown")
        assert result == "unknown"

    def test_enum_to_value_with_already_value(self):
        """Test passing string value directly"""
        result = enum_to_value("Intake")
        assert result == "Intake"

    def test_enum_to_value_with_different_enums(self):
        """Test with different enum types"""
        source = MessageSource.DIRECT_MESSAGE
        assert enum_to_value(source) == "Direct Message"
        
        customer_type = CustomerType.SCARCITY_BUYER
        assert enum_to_value(customer_type) == "عميل الندرة"


class TestEnumToName:
    """Test enum_to_name function"""

    def test_enum_to_name_with_valid_enum(self):
        """Test getting enum name"""
        stage = LeadStage.QUALIFIED
        result = enum_to_name(stage)
        assert result == "QUALIFIED"

    def test_enum_to_name_with_none(self):
        """Test getting name from None returns default"""
        result = enum_to_name(None)
        assert result == ""

    def test_enum_to_name_with_none_and_default(self):
        """Test getting name from None with custom default"""
        result = enum_to_name(None, "UNKNOWN")
        assert result == "UNKNOWN"

    def test_enum_to_name_with_string_value(self):
        """Test passing string directly"""
        result = enum_to_name("test")
        assert result == "test"


class TestSafeEnumComparison:
    """Test safe_enum_comparison function"""

    def test_comparison_with_matching_value(self):
        """Test comparison when values match"""
        stage = LeadStage.INTAKE
        result = safe_enum_comparison(stage, "Intake")
        assert result is True

    def test_comparison_with_non_matching_value(self):
        """Test comparison when values don't match"""
        stage = LeadStage.INTAKE
        result = safe_enum_comparison(stage, "Qualified")
        assert result is False

    def test_comparison_with_none(self):
        """Test comparison with None returns False"""
        result = safe_enum_comparison(None, "Intake")
        assert result is False

    def test_comparison_with_string_value(self):
        """Test comparison with already-string value"""
        result = safe_enum_comparison("Intake", "Intake")
        assert result is True


class TestIntegrationWithModels:
    """Integration tests with actual database usage patterns"""

    def test_typical_api_response_pattern(self):
        """Test pattern used in API responses"""
        # Simulate what happens in Server/routes/api.py
        lead_stage = LeadStage.IN_PROGRESS
        customer_type = CustomerType.EMOTIONAL_BUYER
        message_source = None
        
        response = {
            "lead_stage": enum_to_value(lead_stage),
            "customer_type": enum_to_value(customer_type),
            "message_source": enum_to_value(message_source)
        }
        
        assert response["lead_stage"] == "In-Progress"
        assert response["customer_type"] == "عميل العاطفة"
        assert response["message_source"] is None

    def test_comparison_for_filtering(self):
        """Test pattern used for filtering"""
        stages = [LeadStage.INTAKE, LeadStage.QUALIFIED, None, LeadStage.CONVERTED]
        
        # Filter for specific stage
        intake_count = sum(1 for s in stages if safe_enum_comparison(s, "Intake"))
        assert intake_count == 1
        
        # Count None values
        none_count = sum(1 for s in stages if s is None)
        assert none_count == 1

    def test_type_safety_improvement(self):
        """Test that new approach is type-safe"""
        # Old pattern: getattr(enum, 'value', None)
        # New pattern: enum_to_value(enum)
        
        stage = LeadStage.QUALIFIED
        
        # Both should work but new is type-safe
        old_pattern = getattr(stage, 'value', None)
        new_pattern = enum_to_value(stage)
        
        assert old_pattern == new_pattern == "Qualified"
        
        # With None, new pattern is cleaner
        stage_none = None
        assert enum_to_value(stage_none) is None
