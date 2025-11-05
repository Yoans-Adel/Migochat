import logging
from typing import Dict, Optional, Any
from database import Message, MessageSource, PostType, Post, AdCampaign, MessageDirection
from database.context import get_db_session
from datetime import datetime, timedelta, timezone
import json

logger = logging.getLogger(__name__)


class MessageSourceTracker:
    def __init__(self) -> None:
        pass

    def detect_message_source(self, webhook_data: Dict[str, Any], psid: str) -> MessageSource:
        """Detect the source of incoming message"""
        try:
            # Check if message is from an ad
            if self._is_from_ad(webhook_data):
                return MessageSource.AD

            # Check if message is from a comment conversion
            if self._is_from_comment(webhook_data):
                return MessageSource.COMMENT

            # Check if user is existing customer
            if self._is_existing_customer(psid):
                return MessageSource.EXISTING_CUSTOMER

            # Default to direct message
            return MessageSource.DIRECT_MESSAGE

        except Exception as e:
            logger.error(f"Error detecting message source: {e}")
            return MessageSource.DIRECT_MESSAGE

    def _is_from_ad(self, webhook_data: Dict[str, Any]) -> bool:
        """Check if message originated from an advertisement"""
        try:
            for entry in webhook_data.get("entry", []):
                for event in entry.get("messaging", []):
                    # Check for ad referral data
                    if "referral" in event:
                        referral = event["referral"]
                        if referral.get("source") == "ADS":
                            return True

                    # Check for ad_id in metadata
                    if "message" in event and "ad_id" in event["message"]:
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking ad source: {e}")
            return False

    def _is_from_comment(self, webhook_data: Dict[str, Any]) -> bool:
        """Check if message originated from a comment"""
        try:
            for entry in webhook_data.get("entry", []):
                for event in entry.get("messaging", []):
                    # Check for comment referral
                    if "referral" in event:
                        referral = event["referral"]
                        if referral.get("source") == "COMMENT":
                            return True

                    # Check for post_id indicating comment conversion
                    if "message" in event and "post_id" in event["message"]:
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking comment source: {e}")
            return False

    def _is_existing_customer(self, psid: str) -> bool:
        """Check if user is an existing customer"""
        try:
            # Check if user has previous messages
            with get_db_session() as db:
                # Query messages directly using user PSID
                previous_messages = db.query(Message).filter(
                    Message.sender_id == psid,
                    Message.direction == MessageDirection.INBOUND
                ).count()

                return previous_messages > 1  # More than just the current message

        except Exception as e:
            logger.error(f"Error checking existing customer: {e}")
            return False

    def extract_post_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract post-related data from webhook"""
        try:
            post_data = {
                "post_id": None,
                "post_type": None,
                "post_price": None,
                "post_data": None,
                "comment_id": None,
                "ad_id": None
            }

            for entry in webhook_data.get("entry", []):
                for event in entry.get("messaging", []):
                    # Extract referral data
                    if "referral" in event:
                        referral = event["referral"]
                        post_data["post_id"] = referral.get("ref")
                        post_data["comment_id"] = referral.get("comment_id")
                        post_data["ad_id"] = referral.get("ad_id")

                    # Extract message metadata
                    if "message" in event:
                        message = event["message"]
                        post_data["post_id"] = message.get("post_id")
                        post_data["comment_id"] = message.get("comment_id")
                        post_data["ad_id"] = message.get("ad_id")

            return post_data

        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return {}

    def get_post_info(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post information from database"""
        try:
            with get_db_session() as db:
                post = db.query(Post).filter(Post.facebook_post_id == post_id).first()
                if post:
                    return {
                        "post_id": post.facebook_post_id,
                        "post_type": post.post_type.value if post.post_type else None,
                        "post_content": post.post_content,
                        "post_price": post.post_price,
                        "post_data": json.loads(post.post_data) if post.post_data else None,
                        "created_at": post.created_at.isoformat()
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting post info: {e}")
            return None

    def get_ad_info(self, ad_id: str) -> Optional[Dict[str, Any]]:
        """Get ad campaign information from database"""
        try:
            with get_db_session() as db:
                ad = db.query(AdCampaign).filter(AdCampaign.facebook_ad_id == ad_id).first()
                if ad:
                    return {
                        "ad_id": ad.facebook_ad_id,
                        "campaign_name": ad.campaign_name,
                        "ad_content": ad.ad_content,
                        "target_audience": json.loads(ad.target_audience) if ad.target_audience else None,
                        "budget": ad.budget,
                        "status": ad.status,
                        "created_at": ad.created_at.isoformat()
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting ad info: {e}")
            return None

    def create_post(self, facebook_post_id: str, post_type: PostType,
                    content: str, price: Optional[str] = None, 
                    data: Optional[Dict[str, Any]] = None) -> Optional[Post]:
        """Create a new post record"""
        try:
            with get_db_session() as db:
                post = Post(
                    facebook_post_id=facebook_post_id,
                    post_type=post_type,
                    post_content=content,
                    post_price=price,
                    post_data=json.dumps(data) if data else None,
                    created_at=datetime.now(timezone.utc)
                )

                db.add(post)
                db.commit()
                db.refresh(post)

                logger.info(f"Created post record: {facebook_post_id}")
                return post

        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None

    def create_ad_campaign(self, facebook_ad_id: str, campaign_name: str,
                           content: str, target_audience: Optional[Dict[str, Any]] = None,
                           budget: Optional[str] = None) -> Optional[AdCampaign]:
        """Create a new ad campaign record"""
        try:
            with get_db_session() as db:
                ad = AdCampaign(
                    facebook_ad_id=facebook_ad_id,
                    campaign_name=campaign_name,
                    ad_content=content,
                    target_audience=json.dumps(target_audience) if target_audience else None,
                    budget=budget,
                    created_at=datetime.now(timezone.utc)
                )

                db.add(ad)
                db.commit()
                db.refresh(ad)

                logger.info(f"Created ad campaign record: {facebook_ad_id}")
                return ad

        except Exception as e:
            logger.error(f"Error creating ad campaign: {e}")
            return None

    def get_message_source_analytics(self) -> Dict[str, Any]:
        """Get analytics for message sources"""
        try:
            with get_db_session() as db:
                # Count messages by source
                source_counts: Dict[str, int] = {}
                for source in MessageSource:
                    count = db.query(Message).filter(Message.message_source == source).count()
                    source_counts[source.value] = count

                # Count messages by post type
                post_type_counts: Dict[str, int] = {}
                for post_type in PostType:
                    count = db.query(Message).filter(Message.post_type == post_type).count()
                    post_type_counts[post_type.value] = count

                # Recent activity by source (last 24 hours)
                yesterday = datetime.now(timezone.utc) - timedelta(days=1)
                recent_by_source: Dict[str, int] = {}
                for source in MessageSource:
                    count = db.query(Message).filter(
                        Message.message_source == source,
                        Message.timestamp >= yesterday
                    ).count()
                    recent_by_source[source.value] = count

                return {
                    "source_distribution": source_counts,
                    "post_type_distribution": post_type_counts,
                    "recent_activity": recent_by_source,
                    "total_messages": db.query(Message).count()
                }

        except Exception as e:
            logger.error(f"Error getting message source analytics: {e}")
            return {}
