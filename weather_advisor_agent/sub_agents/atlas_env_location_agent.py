from ..config import config

from google.adk.agents import LoopAgent
from google.adk.agents import Agent

from google.adk.tools import FunctionTool
from google.adk.tools import google_search

from ..validation_checkers import EnvLocationGeoValidationChecker

from ..utils import atlas_location_callback

from ..tools.web_access_tools import geocode_place_name

from ..utils.observability import observability

atlas_env_location_geocode_agent = Agent(
  model=config.worker_model,
  name="atlas_env_location_geocode_agent",
  description="Converts discovered location names into coordinates.",
  instruction="""
  You are Atlas-Geocoder.

  Steps:
  1. Read `env_location_options` from session state.
    Each entry looks like:
      { "name": "...", "region_hint": "...", "activity": "..." }

  2. For each entry, call geocode_place_name to get:
    - latitude, longitude
    - region info
    - country
    - admin1 (state)

  3. Rewrite env_location_options to:
    [
      {
        "name": <place>,
        "latitude": <float>,
        "longitude": <float>,
        "country": <str or None>,
        "admin1": <str or None>,
        "activity": <original activity>,
        "source": "discovery+geocode"
      },
      ...
    ]

  Rules:
  - Produce no guesses.
  - Use ONLY real geocode results.
  """,
  tools=[FunctionTool(geocode_place_name)],
  output_key="env_location_options",
  after_agent_callback=atlas_location_callback
)


atlas_env_location_discovery_agent = Agent(
  model=config.worker_model,
  name="atlas_env_location_discovery_agent",
  description="Finds nearby candidate locations for outdoor activities.",
  instruction="""
  You are Atlas-Discovery.

  Input:
  - A user's general location (city/region/country).
  - An outdoor activity (hiking, trail running, cycling, etc).

  Task:
  1. Infer the activity.
  2. Use google_search to find **real, verifiable locations nearby**.
  3. Produce 3–7 candidate locations.
  4. Write to session state key `env_location_options` a list like:
    [
      {"name": "...", "region_hint": "...", "activity": "..."},
      ...
    ]

  Notes:
  - Do not fabricate locations.
  - Results must come from the search tool.
  """,
  tools=[google_search],
  output_key="env_location_options",
  after_agent_callback=atlas_location_callback,
)

robust_env_location_agent = LoopAgent(
  name="atlas_env_location_loop_agent",
  description="Runs the Atlas location pipeline: discovery → geocode → validation.",
  sub_agents=[atlas_env_location_discovery_agent,atlas_env_location_geocode_agent,EnvLocationGeoValidationChecker(name="location_geo_validation_agent")],
  max_iterations=3
)
