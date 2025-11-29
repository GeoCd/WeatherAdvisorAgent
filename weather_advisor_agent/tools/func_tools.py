import re
import json
import logging
from typing import Dict, Any

from weather_advisor_agent.tools.web_access_tools import fetch_env_snapshot_from_open_meteo

logger = logging.getLogger(__name__)
_last_snapshot = None

def fetch_and_store_snapshot(latitude: float, longitude: float) -> Dict[str, Any]:
  """Wrapper for fetch_env_snapshot_from_open_meteo"""
  global _last_snapshot
  _last_snapshot = fetch_env_snapshot_from_open_meteo(latitude, longitude)
  logger.debug(f"Stored snapshot in global cache for ({latitude}, {longitude})")
  return _last_snapshot


def get_last_snapshot() -> Dict[str, Any]:
  """Retrieve last snapshot"""
  global _last_snapshot
  snapshot = _last_snapshot
  _last_snapshot = None
  return snapshot

#Deprecated function, keeping for documentation and test purposes
def parse_json_string(value: str) -> any:
  """Parse JSON string, removing markdown code blocks"""
  if not isinstance(value, str):
    return value
  
  value = re.sub(r'```json\s*', '', value)
  value = re.sub(r'```\s*', '', value)
  value = value.strip()
  
  try:
    parsed = json.loads(value)
    return parsed
  except json.JSONDecodeError as e:
    logger.debug(f"JSON parse failed: {e}.\n")
    return value