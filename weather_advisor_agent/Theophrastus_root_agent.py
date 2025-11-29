import json
import logging
import datetime

from google.adk.agents import Agent
from google.genai.types import Content, Part
from google.adk.tools import FunctionTool

from weather_advisor_agent.config import config

from weather_advisor_agent.sub_agents import (robust_env_data_agent,
  robust_env_risk_agent,
  robust_env_location_agent
)

from weather_advisor_agent.memory import TheophrastusMemory

from weather_advisor_agent.tools.creation_tools import save_env_report_to_file


logger = logging.getLogger(__name__)

def Theophrastus_root_callback(*args, **kwargs):
  snapshot = {}
  ctx = kwargs.get("callback_context")
  if ctx is None and len(args) >= 2:
    ctx = args[1]
  if ctx is None:
    return None
  
  state = ctx.session.state

  advice = state.get("env_advice_markdown")
  if advice:
    return Content(parts=[Part(text=advice)])

  for key in ["env_snapshot", "env_location_options", "env_risk_report", "env_advice_markdown"]:
    if key in state:
      snapshot[key] = state[key]
  state["_evaluation_snapshot"] = snapshot

  risk_report = state.get("env_risk_report")
  if risk_report and not advice:
    return None

  locs = state.get("env_location_options")
  if isinstance(locs, str):
    try:
      locs = json.loads(locs)
    except:
      pass
  
  if isinstance(locs, list) and locs and isinstance(locs[0], dict):
    last_msg = state.get("last_user_message", "").lower()
    report_keywords = ["generate", "create", "write", "make", "report", "recommendations", "analysis"]
    
    if not any(keyword in last_msg for keyword in report_keywords):
      lines = [f"- {loc.get('name','Unknown')} — {loc.get('admin1','')}, {loc.get('country','')}" for loc in locs]
      msg = "Here are some options you might consider:\n" + "\n".join(lines)
      return Content(parts=[Part(text=msg)])

  return None

Theophrastus_root_agent = Agent(
  name="envi_root_agent",
  model=config.worker_model,
  description="Interactive environmental intelligence assistant.",
  instruction=f"""
  You are Theophrastus, an environmental intelligence assistant.

  MEMORY CAPABILITIES:
    - You remember user preferences (activities, risk tolerance, favorite locations).
    - You track recently queried locations.
    - You learn from user patterns over time.

  When a user returns, you can reference their:
    - Favorite activities: {TheophrastusMemory.get_user_preference("current_user")}
    - Recent locations: {TheophrastusMemory.get_recent_locations("current_user")}

  You update memory whenever the user mentions:
    - Activities they enjoy.
    - Locations they visit frequently.
    - Their comfort level with environmental risks.

  Your goals:
    - Help users understand weather and environmental conditions.
    - Estimate environmental risks (heat, cold, wind, air quality).
    - Provide safe, practical recommendations.
    - Suggest suitable outdoor activities when relevant.

  You have access to INTERNAL state fields (environmental snapshot, risk report,
  location options, markdown report). These MUST NEVER be mentioned to the user.

  ============================================================
  ================ CRITICAL AGENT SEQUENCE ===================
  ============================================================

  For ANY weather query (including simple ones like "What's the weather?"):
  
  STEP 1: Call robust_env_data_agent
  STEP 2: Call robust_env_risk_agent
  STEP 3: Call aurora_env_advice_writer
  STEP 4: Return nothing (callback handles response)

  This sequence is MANDATORY for:
  - "What's the weather in [place]?"
  - "How is the weather?"
  - "What are the conditions?"
  - "Generate a report"
  - "What's the weather like in those locations?"
  
  ALL weather queries require ALL THREE agents.

  ============================================================
  =================== LOCATION QUERIES =======================
  ============================================================

  For location queries ("find locations", "where to go"):
  
  STEP 1: Call robust_env_location_agent
  STEP 2: Return nothing (callback handles response)

  ============================================================
  ===================== ABSOLUTELY FORBIDDEN =================
  ============================================================

  You MUST NEVER:
  - Output raw JSON
  - Output weather data yourself
  - Output risk assessments yourself
  - Skip aurora_env_advice_writer after calling robust_env_risk_agent
  - Return anything after calling aurora_env_advice_writer

  The callback handles ALL user responses.
  Your ONLY job is to call the right agents in the right order.

  ============================================================
  ========================= EXAMPLES =========================
  ============================================================

  User: "How is the weather in Sacramento?"
  You: Call robust_env_data_agent → robust_env_risk_agent → aurora_env_advice_writer
  You: Return nothing
  Callback: Shows markdown report

  User: "What is the weather like in those locations?"
  You: Call robust_env_data_agent → robust_env_risk_agent → aurora_env_advice_writer
  You: Return nothing
  Callback: Shows markdown report

  User: "Generate a recommendations report"
  You: Call robust_env_data_agent → robust_env_risk_agent → aurora_env_advice_writer
  You: Return nothing
  Callback: Shows markdown report

  User: "Find hiking locations near Mexico City"
  You: Call robust_env_location_agent
  You: Return nothing
  Callback: Shows location list

  ============================================================

  Remember: EVERY weather query needs ALL THREE agents.
  After robust_env_risk_agent, ALWAYS call aurora_env_advice_writer.

  Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
  """,
  sub_agents=[
    robust_env_location_agent,
    robust_env_data_agent,
    robust_env_risk_agent  # This now includes Aurora as its final step
  ],
  tools=[FunctionTool(save_env_report_to_file)],
  after_agent_callback=Theophrastus_root_callback
)