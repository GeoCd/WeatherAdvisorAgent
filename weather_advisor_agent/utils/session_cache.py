import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)

_session_cache: Dict[str, Dict[str, Any]] = {}

def store_evaluation_data(session_id: str, data: Dict[str, Any]) -> None:
    """Store evaluation data for a session"""
    if session_id not in _session_cache:
        _session_cache[session_id] = {}
    
    _session_cache[session_id].update(data)
    logger.debug(f"Cached {list(data.keys())} for session {session_id}.")


def get_evaluation_data(session_id: str) -> Dict[str, Any]:
    """Retrieve evaluation data for a session"""
    data = _session_cache.get(session_id, {}).copy()
    logger.info(f"Retrieved {len(data)} keys from cache for session {session_id}.")
    return data


def clear_session(session_id: str) -> None:
    """Clear evaluation data for a specific session"""
    if session_id in _session_cache:
        del _session_cache[session_id]
        logger.debug(f"Cleared cache for session {session_id}.")


def clear_all() -> None:
    """Clear all cached evaluation data"""
    _session_cache.clear()
    logger.debug("Cleared all session cache.")