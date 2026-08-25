"""
Logging utility for AyurPedia.
Handles audit logging for DPDP compliance.
"""

import logging
import json
from datetime import datetime
from typing import Optional, List
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log file path
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "audit.log"


def log_interaction(
    user_id: Optional[str],
    query: str,
    jurisdiction: str,
    response: str,
    citations: List[str],
    confidence: str
) -> None:
    """Log interaction for audit purposes.
    
    Args:
        user_id: Optional user identifier (hashed if provided)
        query: User query
        jurisdiction: Jurisdiction used
        response: Generated response
        citations: List of citations
        confidence: Confidence level
    """
    try:
        # Ensure log directory exists
        LOG_DIR.mkdir(exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,  # Should be hashed if provided
            "query": query[:500],  # Truncate for privacy
            "jurisdiction": jurisdiction,
            "response": response[:1000],  # Truncate for privacy
            "citations_count": len(citations),
            "confidence": confidence
        }
        
        # Write to log file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(f"Interaction logged: query='{query[:50]}...'")
        
    except Exception as e:
        logger.warning(f"Failed to log interaction: {e}")


def get_recent_logs(limit: int = 100) -> List[dict]:
    """Get recent log entries.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of log entries
    """
    try:
        if not LOG_FILE.exists():
            return []
        
        logs = []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        
        # Return most recent logs
        return logs[-limit:]
        
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return []
