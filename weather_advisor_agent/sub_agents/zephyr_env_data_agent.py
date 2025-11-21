from ..config import config

import logging

from google.genai.types import Content
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool

from ..tools.web_access_tools import (fetch_env_snapshot_from_open_meteo,geocode_place_name)

from ..validation_checkers import EnvSnapshotValidationChecker

from ..utils.observability import observability

logger = logging.getLogger(__name__)
_last_snapshot = None

def fetch_and_store_snapshot(latitude: float, longitude: float):
  global _last_snapshot
  _last_snapshot = fetch_env_snapshot_from_open_meteo(latitude, longitude)
  return _last_snapshot

def zephyr_callback_from_global(callback_context: CallbackContext) -> Content:
  global _last_snapshot
  
  if _last_snapshot:
    callback_context.session.state["env_snapshot"] = _last_snapshot
    observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=True)
    logger.info("Stored snapshot. | ")
    
    if isinstance(_last_snapshot, dict) and "current" in _last_snapshot:
      current = _last_snapshot["current"]
      temp = current.get("temperature_c", "?")
      wind = current.get("wind_speed_10m_ms", "?")
      logger.info(f"Data: {temp}°C, {wind} m/s wind. | ")
    
    _last_snapshot = None
  else:
    callback_context.session.state["env_snapshot"] = {}
    observability.log_agent_complete("zephyr_env_data_agent","env_snapshot",success=False)
    logger.warning("No snapshot. | ")
  
  return Content()


zephyr_env_data_agent = Agent(
  model=config.worker_model,
  name="zephyr_env_data_agent",
  description="Fetches live environmental data.",
  instruction="""
  Extract location from user message.
  Call geocode_place_name, then call fetch_and_store_snapshot with coordinates.
  """,
  tools=[FunctionTool(fetch_and_store_snapshot),FunctionTool(geocode_place_name)],
  after_agent_callback=zephyr_callback_from_global
)

robust_env_data_agent = LoopAgent(
  name="robust_env_data_agent",
  description="Robust environmental data fetcher with retries.",
  sub_agents=[zephyr_env_data_agent,EnvSnapshotValidationChecker(name="env_snapshot_validation_checker")],
  max_iterations=config.max_iterations
)