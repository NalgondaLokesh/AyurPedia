"""
Sentry error tracking integration for AyurPedia.
"""

import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .config import get_config

logger = logging.getLogger(__name__)

# Try to import MongoIntegration, but make it optional
try:
    from sentry_sdk.integrations.mongodb import MongoIntegration
    MONGO_INTEGRATION_AVAILABLE = True
except ImportError:
    MONGO_INTEGRATION_AVAILABLE = False
    logger.warning("MongoIntegration not available in sentry_sdk. MongoDB error tracking will be limited.")


def init_sentry():
    """Initialize Sentry error tracking."""
    config = get_config()
    
    if not config.sentry_dsn:
        logger.info("Sentry DSN not configured. Error tracking disabled.")
        return
    
    try:
        integrations = [
            FastApiIntegration(),
            RedisIntegration(),
        ]
        
        # Only add MongoIntegration if available
        if MONGO_INTEGRATION_AVAILABLE:
            integrations.append(MongoIntegration())
        
        sentry_sdk.init(
            dsn=config.sentry_dsn,
            integrations=integrations,
            traces_sample_rate=0.1,  # 10% of transactions sampled
            environment="development" if "localhost" in config.qdrant_url else "production",
            release="ayurpedia@2.0.0",
            beforeSend=before_send,
        )
        logger.info("Sentry error tracking initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def before_send(event, hint):
    """Filter events before sending to Sentry."""
    # Filter out 404 errors
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]
        if hasattr(exc_value, "status_code") and exc_value.status_code == 404:
            return None
    
    # Add custom context
    if event.get("request"):
        event["request"]["url"] = event["request"].get("url", "")
    
    return event


def capture_exception(exception):
    """Capture an exception and send to Sentry."""
    if sentry_sdk.Hub.current.client:
        sentry_sdk.capture_exception(exception)


def capture_message(message, level="info"):
    """Capture a message and send to Sentry."""
    if sentry_sdk.Hub.current.client:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id, email=None, username=None):
    """Set user context for Sentry."""
    if sentry_sdk.Hub.current.client:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username,
        })
