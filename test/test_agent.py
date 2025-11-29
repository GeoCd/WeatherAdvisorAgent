import asyncio
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from weather_advisor_agent import Theophrastus_root_agent
from weather_advisor_agent.utils import Theophrastus_Observability

APP_NAME = "Theophrastus_app"
USER_ID = "test_user"
SESSION_ID = "test_Theophrastus"

def _looks_like_env_snapshot_json(text: str) -> bool:
  if not text:
    return False
  
  t = text.strip()

  if not t.startswith("{"):
    return False

  suspicious_keys = ['"current"', '"hourly"', '"location"', '"raw"']
  return any(k in t for k in suspicious_keys)


async def main():
  session_service = InMemorySessionService()
  await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
  )
  runner = Runner(
    agent=Theophrastus_root_agent,
    app_name=APP_NAME,
    session_service=session_service
  )

  queries = [
    "How is the weather in my city Nezahualcoyotl, Mexico State?",
    "I want to see the snow this weekend near Madrid. What are some good locations?",
    "What is the weather like in those locations?",
    "Generate a recommendations report.",
    "Save it as 'Madrid'"
  ]

  logging.getLogger("google_genai.types").setLevel(logging.ERROR)

  print("="*80)
  print("THEOPHRASTUS AGENT TEST WITH OBSERVABILITY, LOGGING & MEMORY")
  print("="*80)

  for i, query in enumerate(queries, 1):
    print(f"{'='*80}")
    print(f"\n>>> USER: {query}\n")
    print(f"{'='*80}")
    last_user_facing_text = None

    with Theophrastus_Observability.trace_operation(f"user_query_{i}",attributes={"query": query[:50]}):
      async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=genai_types.Content(role="user",parts=[genai_types.Part.from_text(text=query)])
      ):
        if not event.is_final_response():
          continue
        content = getattr(event, "content", None)
        if not content:
          continue
        parts = getattr(content, "parts", None)
        if not parts:
          continue
        for part in parts:
          text = getattr(part, "text", None)
          if not text:
            continue
          if _looks_like_env_snapshot_json(text):
            continue

          last_user_facing_text = text

    print(f"\n{"="*80}\n")
    if last_user_facing_text:
        print(f">>> THEOPHRASTUS: {last_user_facing_text}")
    else:
      print(">>> THEOPHRASTUS: [No user-facing text in response]\n")
    print(f"\n{"="*80}\n")

  Theophrastus_Observability.print_metrics_summary()

  Theophrastus_Observability.export_metrics("test")

  Theophrastus_Observability.export_traces("test")

  print("\n" + "="*80)
  print("TEST RUN COMPLETE")
  print("="*80)

if __name__ == "__main__":
    asyncio.run(main())