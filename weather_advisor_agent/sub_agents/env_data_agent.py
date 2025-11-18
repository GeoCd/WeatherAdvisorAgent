from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool
from typing import Dict, Any

from ..config import config
from ..agent_utils import suppress_output_callback
from ..tools import (
    fetch_env_snapshot_from_open_meteo,
    geocode_place_name,
)
from ..validation_checkers import EnvSnapshotValidationChecker


env_data_agent = Agent(
    model=config.worker_model,
    name="env_data_agent",
    description="Fetches live environmental data (weather & basic air metrics) for one or more locations.",
    instruction="""
    You are Zephyr, a data-gathering specialist for environmental intelligence.

    Your job:

    - Given the user's request, determine what location(s) are relevant.
      The user may provide:
        * A city name (e.g. "Ciudad de México", "Berlin").
        * A region/state (e.g. "Morelos", "California").
        * A specific place name (e.g. "Lago de Tequesquitengo").
        * Or explicit coordinates (latitude and longitude).

    - ALWAYS follow this order of preference:
      1. If the user gives a city/place/region name, call the `geocode_place_name`
         tool to retrieve approximate coordinates.
         - If multiple results are returned, pick the one that best fits the
           context (same country/region as the user if possible).
         - Do not invent coordinates.
      2. Only if geocoding fails or returns no results, ask the user to provide
         approximate coordinates (latitude and longitude) as a fallback.

    - Once you have a (latitude, longitude) pair for each target location,
      call the `fetch_env_snapshot_from_open_meteo` tool to get a weather
      snapshot for that point.
      Store the resulting snapshot in the `env_snapshot` state key.
      If there are multiple locations, you may store a list of snapshots with
      the associated location names.

    Constraints:
    - Never fabricate numeric values; always rely on `geocode_place_name` and
      `fetch_env_snapshot_from_open_meteo`.
    - If geocoding is ambiguous (e.g. multiple cities with the same name),
      ask a brief clarification (country/region) before proceeding.
    """,
    tools=[
        FunctionTool(fetch_env_snapshot_from_open_meteo),
        FunctionTool(geocode_place_name),
    ],
    output_key="env_snapshot",
    after_agent_callback=suppress_output_callback,
)


robust_env_data_agent = LoopAgent(
    name="robust_env_data_agent",
    description="A robust environmental data fetcher that retries if it fails.",
    sub_agents=[
        env_data_agent,
        EnvSnapshotValidationChecker(name="env_snapshot_validation_checker"),
    ],
    max_iterations=config.max_iterations,
    after_agent_callback=suppress_output_callback)

