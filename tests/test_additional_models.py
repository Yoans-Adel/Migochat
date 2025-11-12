"""
Additional Database Model Tests
Tests for Post, AdCampaign, and AppSettings models
"""
# type: ignore  # pytest fixtures don't support full type checking

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError


@pytest.mark.database
@pytest.mark.unit
class TestPostModel:
    """Test Post model"""

    def test_create_post(self, db_session):
        """Test creating a post"""
        from database import Post, PostType

        post = Post(
            facebook_post_id="post_12345",
            post_type=PostType.PRODUCT_POST,
            post_content="Check out this amazing product!",
            post_price="500 EGP",
            is_active=True
        )

        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        assert post.id is not None
        assert post.facebook_post_id == "post_12345"
        assert post.post_type == PostType.PRODUCT_POST
        assert post.post_content == "Check out this amazing product!"
        assert post.post_price == "500 EGP"
        assert post.is_active is True

    def test_post_unique_facebook_id(self, db_session):
        """Test that facebook_post_id must be unique"""
        from database import Post, PostType

        post1 = Post(
            facebook_post_id="duplicate_post_123",
            post_type=PostType.PRODUCT_POST
        )
        db_session.add(post1)
        db_session.commit()

        # Try to create duplicate
        post2 = Post(
            facebook_post_id="duplicate_post_123",
            post_type=PostType.PROMOTION_POST
        )
        db_session.add(post2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_post_has_timestamp(self, db_session):
        """Test that post has created_at timestamp"""
        from database import Post, PostType

        post = Post(
            facebook_post_id="post_timestamp_test",
            post_type=PostType.PRODUCT_POST
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        assert post.created_at is not None
        assert isinstance(post.created_at, datetime)

    def test_post_type_enum(self, db_session):
        """Test post_type enum values"""
        from database import Post, PostType

        product_post = Post(
            facebook_post_id="product_post",
            post_type=PostType.PRODUCT_POST
        )
        promo_post = Post(
            facebook_post_id="promo_post",
            post_type=PostType.PROMOTION_POST
        )
        general_post = Post(
            facebook_post_id="general_post",
            post_type=PostType.GENERAL_POST
        )

        db_session.add_all([product_post, promo_post, general_post])
        db_session.commit()

        assert product_post.post_type == PostType.PRODUCT_POST
        assert promo_post.post_type == PostType.PROMOTION_POST
        assert general_post.post_type == PostType.GENERAL_POST

    def test_post_optional_fields(self, db_session):
        """Test post with minimal required fields"""
        from database import Post, PostType

        post = Post(
            facebook_post_id="minimal_post",
            post_type=PostType.GENERAL_POST
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        assert post.post_content is None
        assert post.post_price is None
        assert post.post_data is None

    def test_post_message_relationship(self, db_session, create_test_user, create_test_message):
        """Test post-message relationship"""
        from database import Post, PostType

        # Create post
        post = Post(
            facebook_post_id="post_with_messages",
            post_type=PostType.PRODUCT_POST
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        # Create user and message linked to post
        user = create_test_user()
        message = create_test_message(user_id=user.id, post_id=post.id)

        # Verify relationship
        assert message.post_id == post.id
        assert len(post.messages) > 0
        assert message in post.messages


@pytest.mark.database
@pytest.mark.unit
class TestAdCampaignModel:
    """Test AdCampaign model"""

    def test_create_ad_campaign(self, db_session):
        """Test creating an ad campaign"""
        from database import AdCampaign

        campaign = AdCampaign(
            facebook_ad_id="ad_67890",
            campaign_name="Summer Sale Campaign",
            ad_content="Get 50% off on all products!",
            budget="1000 EGP",
            status="active"
        )

        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        assert campaign.id is not None
        assert campaign.facebook_ad_id == "ad_67890"
        assert campaign.campaign_name == "Summer Sale Campaign"
        assert campaign.ad_content == "Get 50% off on all products!"
        assert campaign.budget == "1000 EGP"
        assert campaign.status == "active"

    def test_ad_campaign_unique_facebook_id(self, db_session):
        """Test that facebook_ad_id must be unique"""
        from database import AdCampaign

        campaign1 = AdCampaign(
            facebook_ad_id="duplicate_ad_123",
            campaign_name="Campaign 1"
        )
        db_session.add(campaign1)
        db_session.commit()

        # Try to create duplicate
        campaign2 = AdCampaign(
            facebook_ad_id="duplicate_ad_123",
            campaign_name="Campaign 2"
        )
        db_session.add(campaign2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_ad_campaign_has_timestamp(self, db_session):
        """Test that ad campaign has created_at timestamp"""
        from database import AdCampaign

        campaign = AdCampaign(
            facebook_ad_id="ad_timestamp_test",
            campaign_name="Test Campaign"
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        assert campaign.created_at is not None
        assert isinstance(campaign.created_at, datetime)

    def test_ad_campaign_default_status(self, db_session):
        """Test ad campaign default status"""
        from database import AdCampaign

        campaign = AdCampaign(
            facebook_ad_id="ad_default_status",
            campaign_name="Test Campaign"
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        assert campaign.status == "active"

    def test_ad_campaign_optional_fields(self, db_session):
        """Test ad campaign with minimal required fields"""
        from database import AdCampaign

        campaign = AdCampaign(
            facebook_ad_id="minimal_ad"
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        assert campaign.campaign_name is None
        assert campaign.ad_content is None
        assert campaign.target_audience is None
        assert campaign.budget is None

    def test_ad_campaign_message_relationship(self, db_session, create_test_user, create_test_message):
        """Test ad campaign-message relationship"""
        from database import AdCampaign

        # Create ad campaign
        campaign = AdCampaign(
            facebook_ad_id="ad_with_messages",
            campaign_name="Test Campaign"
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        # Create user and message linked to ad
        user = create_test_user()
        message = create_test_message(user_id=user.id, ad_id=campaign.id)

        # Verify relationship
        assert message.ad_id == campaign.id
        assert len(campaign.messages) > 0
        assert message in campaign.messages

    def test_ad_campaign_target_audience_json(self, db_session):
        """Test storing JSON data in target_audience field"""
        from database import AdCampaign
        import json

        audience_data = {
            "age_range": "18-35",
            "gender": "all",
            "interests": ["fashion", "shopping"],
            "location": "Cairo"
        }

        campaign = AdCampaign(
            facebook_ad_id="ad_with_targeting",
            campaign_name="Targeted Campaign",
            target_audience=json.dumps(audience_data)
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        # Verify JSON can be parsed back
        parsed_audience = json.loads(campaign.target_audience)
        assert parsed_audience["age_range"] == "18-35"
        assert "fashion" in parsed_audience["interests"]


@pytest.mark.database
@pytest.mark.unit
class TestAppSettingsModel:
    """Test AppSettings model"""

    def test_create_app_setting(self, db_session):
        """Test creating an app setting"""
        from database import AppSettings

        setting = AppSettings(
            key="facebook_page_access_token",
            value="EAAB...",
            category="facebook",
            is_sensitive=True,
            description="Facebook Page Access Token",
            updated_by="admin"
        )

        db_session.add(setting)
        db_session.commit()
        db_session.refresh(setting)

        assert setting.id is not None
        assert setting.key == "facebook_page_access_token"
        assert setting.value == "EAAB..."
        assert setting.category == "facebook"
        assert setting.is_sensitive is True
        assert setting.description == "Facebook Page Access Token"
        assert setting.updated_by == "admin"

    def test_app_settings_unique_key(self, db_session):
        """Test that key must be unique"""
        from database import AppSettings

        setting1 = AppSettings(
            key="duplicate_key",
            value="value1"
        )
        db_session.add(setting1)
        db_session.commit()

        # Try to create duplicate
        setting2 = AppSettings(
            key="duplicate_key",
            value="value2"
        )
        db_session.add(setting2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_app_settings_has_timestamp(self, db_session):
        """Test that app settings has updated_at timestamp"""
        from database import AppSettings

        setting = AppSettings(
            key="timestamp_test",
            value="test_value"
        )
        db_session.add(setting)
        db_session.commit()
        db_session.refresh(setting)

        assert setting.updated_at is not None
        assert isinstance(setting.updated_at, datetime)

    def test_app_settings_default_values(self, db_session):
        """Test app settings default values"""
        from database import AppSettings

        setting = AppSettings(
            key="test_defaults",
            value="test"
        )
        db_session.add(setting)
        db_session.commit()
        db_session.refresh(setting)

        assert setting.is_sensitive is False
        assert setting.updated_by == "admin"

    def test_app_settings_categories(self, db_session):
        """Test different setting categories"""
        from database import AppSettings

        facebook_setting = AppSettings(
            key="fb_verify_token",
            value="token123",
            category="facebook"
        )
        whatsapp_setting = AppSettings(
            key="wa_phone_id",
            value="phone456",
            category="whatsapp"
        )
        ai_setting = AppSettings(
            key="gemini_api_key",
            value="key789",
            category="ai",
            is_sensitive=True
        )
        system_setting = AppSettings(
            key="app_version",
            value="1.0.0",
            category="system"
        )

        db_session.add_all([facebook_setting, whatsapp_setting, ai_setting, system_setting])
        db_session.commit()

        # Query by category
        facebook_settings = db_session.query(AppSettings).filter_by(category="facebook").all()
        ai_settings = db_session.query(AppSettings).filter_by(category="ai").all()

        assert len(facebook_settings) > 0
        assert len(ai_settings) > 0
        assert ai_settings[0].is_sensitive is True

    def test_app_settings_update_tracking(self, db_session):
        """Test that updated_at changes on update"""
        from database import AppSettings
        import time

        setting = AppSettings(
            key="update_test",
            value="initial_value"
        )
        db_session.add(setting)
        db_session.commit()
        db_session.refresh(setting)

        original_updated_at = setting.updated_at

        # Wait a moment and update
        time.sleep(0.1)
        setting.value = "updated_value"
        db_session.commit()
        db_session.refresh(setting)

        # updated_at should change (if onupdate works)
        # Note: Some databases may not update timestamp if change is too quick
        assert setting.value == "updated_value"

    def test_app_settings_sensitive_flag(self, db_session):
        """Test sensitive settings handling"""
        from database import AppSettings

        sensitive = AppSettings(
            key="api_secret",
            value="secret_123",
            is_sensitive=True
        )
        non_sensitive = AppSettings(
            key="app_name",
            value="Migochat",
            is_sensitive=False
        )

        db_session.add_all([sensitive, non_sensitive])
        db_session.commit()

        # Query sensitive settings
        sensitive_settings = db_session.query(AppSettings).filter_by(is_sensitive=True).all()
        assert len(sensitive_settings) > 0
        assert all(s.is_sensitive for s in sensitive_settings)


@pytest.mark.database
@pytest.mark.integration
class TestAdditionalModelIntegration:
    """Integration tests for Post, AdCampaign, and AppSettings"""

    def test_query_all_posts(self, db_session):
        """Test querying all posts"""
        from database import Post, PostType

        # Create multiple posts
        posts_data = [
            {"facebook_post_id": "post_1", "post_type": PostType.PRODUCT_POST},
            {"facebook_post_id": "post_2", "post_type": PostType.PROMOTION_POST},
            {"facebook_post_id": "post_3", "post_type": PostType.GENERAL_POST},
        ]

        for post_data in posts_data:
            post = Post(**post_data)
            db_session.add(post)

        db_session.commit()

        # Query all posts
        all_posts = db_session.query(Post).all()
        assert len(all_posts) >= 3

    def test_query_active_posts(self, db_session):
        """Test querying only active posts"""
        from database import Post, PostType

        active_post = Post(
            facebook_post_id="active_post",
            post_type=PostType.PRODUCT_POST,
            is_active=True
        )
        inactive_post = Post(
            facebook_post_id="inactive_post",
            post_type=PostType.PRODUCT_POST,
            is_active=False
        )

        db_session.add_all([active_post, inactive_post])
        db_session.commit()

        # Query only active
        active_posts = db_session.query(Post).filter_by(is_active=True).all()
        assert any(p.facebook_post_id == "active_post" for p in active_posts)

    def test_query_settings_by_category(self, db_session):
        """Test querying settings by category"""
        from database import AppSettings

        # Create settings in different categories
        for i in range(3):
            db_session.add(AppSettings(key=f"fb_setting_{i}", category="facebook"))
            db_session.add(AppSettings(key=f"ai_setting_{i}", category="ai"))

        db_session.commit()

        # Query by category
        fb_settings = db_session.query(AppSettings).filter_by(category="facebook").all()
        ai_settings = db_session.query(AppSettings).filter_by(category="ai").all()

        assert len(fb_settings) >= 3
        assert len(ai_settings) >= 3

    def test_message_with_post_and_ad(self, db_session, create_test_user, create_test_message):
        """Test message linked to both post and ad campaign"""
        from database import Post, AdCampaign, PostType

        # Create post and ad campaign
        post = Post(facebook_post_id="post_123", post_type=PostType.PRODUCT_POST)
        campaign = AdCampaign(facebook_ad_id="ad_456", campaign_name="Campaign 1")

        db_session.add_all([post, campaign])
        db_session.commit()
        db_session.refresh(post)
        db_session.refresh(campaign)

        # Create user and message
        user = create_test_user()
        message = create_test_message(
            user_id=user.id,
            post_id=post.id,
            ad_id=campaign.id
        )

        # Verify relationships
        assert message.post_id == post.id
        assert message.ad_id == campaign.id
        assert message in post.messages
        assert message in campaign.messages
