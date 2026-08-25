"""
Validation utility for AyurPedia.
Handles input validation and sanitization.
"""

import re
import logging
from typing import Optional


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_query(query: str) -> bool:
    """Validate user query.
    
    Args:
        query: User query to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not query or not query.strip():
        logger.warning("Empty query provided")
        return False
    
    if len(query) < 1:
        logger.warning("Query too short")
        return False
    
    if len(query) > 1000:
        logger.warning("Query too long")
        return False
    
    return True


def validate_jurisdiction(jurisdiction: str) -> bool:
    """Validate jurisdiction value.
    
    Args:
        jurisdiction: Jurisdiction to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_jurisdictions = ["india", "international", "both"]
    
    if not jurisdiction or not jurisdiction.strip():
        logger.warning("Empty jurisdiction provided")
        return False
    
    if jurisdiction.lower() not in valid_jurisdictions:
        logger.warning(f"Invalid jurisdiction: {jurisdiction}")
        return False
    
    return True


def validate_classification(classification: str) -> bool:
    """Validate classification category.
    
    Args:
        classification: Classification to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_classifications = [
        "Classical",
        "Proprietary",
        "Ayurveda-Aahar",
        "Cosmetic",
        "Phytopharmaceutical",
        "Nutraceutical",
        "Unknown"
    ]
    
    if not classification or not classification.strip():
        logger.warning("Empty classification provided")
        return False
    
    if classification not in valid_classifications:
        logger.warning(f"Invalid classification: {classification}")
        return False
    
    return True


def sanitize_input(text: str) -> str:
    """Sanitize input text to remove harmful content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential SQL injection patterns
    text = re.sub(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC)\b)", "", text, flags=re.IGNORECASE)
    
    # Remove potential script injection patterns
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove non-digit characters
    digits = re.sub(r"[^\d]", "", phone)
    
    # Check if it has 10-15 digits
    return 10 <= len(digits) <= 15
