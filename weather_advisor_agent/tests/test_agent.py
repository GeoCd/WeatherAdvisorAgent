import asyncio
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from weather_advisor_agent import root_agent

async def main():
    """Sample dialogue."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="envi_app", user_id="test_user", session_id="test_session")

    runner = Runner(
        agent=root_agent,
        app_name="envi_app",
        session_service=session_service,)

    # Ejemplo de flujo conversacional:
    queries = [
        "I would like to know if today is a good day to go hiking.",
        "Sure. I am currently in Mexico City.",
        "OK, generate a final recommendations report.",
        "reports/today_envi_weather_recomendations.md"]

    logging.getLogger("google_genai.types").setLevel(logging.ERROR)

    for query in queries:
        print(f">>> {query}")
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=genai_types.Content(role="user",parts=[genai_types.Part.from_text(text=query)])):
            if event.is_final_response() and event.content and event.content.parts:
                print("=== FINAL RESPONSE ===")
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        print(part.text)
                    elif getattr(part, "function_call", None):
                        print("[function_call]", part.function_call)
if __name__ == "__main__":
    asyncio.run(main())
