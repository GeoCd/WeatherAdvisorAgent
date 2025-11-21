import logging
import re

from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content

from .observability import observability

logger = logging.getLogger(__name__)

def _parse_json_string(value: str) -> any:
  """Parse JSON string"""
  if not isinstance(value, str):
    return value
  
  value = re.sub(r'```json\s*', '', value)
  value = re.sub(r'```\s*', '', value)


def zephyr_data_callback(callback_context: CallbackContext) -> Content:
  """Callback for Zephyr"""
  snapshot = callback_context.session.state.get("env_snapshot")
  
  if isinstance(snapshot, str):
    logger.warning("Zephyr returned string instead of dict/list.")
    parsed = _parse_json_string(snapshot)
    
    if isinstance(parsed, (dict, list)):
      callback_context.session.state["env_snapshot"] = parsed
      snapshot = parsed
      logger.info("Parsed JSON string.")
    else:
      logger.error(f"Could not parse snapshot.")
  
  if snapshot:
    if isinstance(snapshot, list):
      count = len(snapshot)
      observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=True)
      logger.info(f"Fetched {count} location snapshot.")
    elif isinstance(snapshot, dict):
      observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=True)
      logger.info("Fetched single location snapshot.")
    else:
      observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=False)
      logger.error(f"Unexpected type: {type(snapshot).__name__}")
    
    observability.log_state_change("env_snapshot","SET",f"Type: {type(snapshot).__name__}")
  else:
    observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=False)
    logger.warning("No snapshot")
  
  return Content()


def aether_risk_callback(callback_context: CallbackContext) -> Content:
  """Callback for Aether"""
  risk_report = callback_context.session.state.get("env_risk_report")
  
  if isinstance(risk_report, str):
    logger.warning("Aether returned string instead of dict.")
    parsed = _parse_json_string(risk_report)
    
    if isinstance(parsed, dict):
      callback_context.session.state["env_risk_report"] = parsed
      risk_report = parsed
      logger.info("Parsed JSON string.")
    else:
      logger.error("Could not parse risk report.")

  if risk_report and isinstance(risk_report, dict):
    overall_risk = risk_report.get("overall_risk", "unknown")
    observability.log_agent_complete("aether_env_risk_agent","env_risk_report",success=True)
    logger.info(f"Risk assessment completed.")
    observability.log_state_change("env_risk_report","SET",f"overall_risk={overall_risk}")
  else:
    observability.log_agent_complete("aether_env_risk_agent","env_risk_report",success=False)
    logger.warning("Not a valid risk report.")
  
  return Content()


def atlas_location_callback(callback_context: CallbackContext) -> Content:
  """Callback for Atlas"""
  locations = callback_context.session.state.get("env_location_options")

  if isinstance(locations, str):
    logger.warning("Atlas returned string instead of list.")
    parsed = _parse_json_string(locations)
    
    if isinstance(parsed, list):
      callback_context.session.state["env_location_options"] = parsed
      locations = parsed
      logger.info("Successfully parsed locations.")
    else:
      logger.error("Could not parse locations.")
  
  if locations and isinstance(locations, list):
    count = len(locations)
    observability.log_agent_complete("atlas_env_location_agent","env_location_options",success=True)
    logger.info(f"Found {count} location option.")
    observability.log_state_change("env_location_options","SET",f"{count} location")
  else:
    observability.log_agent_complete("atlas_env_location_agent","env_location_options",success=False)
    logger.warning("No location options.")
  
  return Content()


def aurora_advice_callback(callback_context: CallbackContext) -> Content:
  """Callback for Aurora"""
  advice = callback_context.session.state.get("env_advice_markdown")
  
  if advice and len(advice) > 100:
    observability.log_agent_complete("aurora_env_advice_writer","env_advice_markdown",success=True)
    logger.info(f"Generated advice report ({len(advice)} chars).")
    observability.log_state_change("env_advice_markdown","SET",f"{len(advice)} characters")
  else:
    observability.log_agent_complete("aurora_env_advice_writer","env_advice_markdown",success=False)
    logger.warning("Report too short or missing.")
  
  return Content()