import requests
import time
import logging
from typing import Dict, List, Any, cast

from weather_advisor_agent.utils.observability import observability

logger = logging.getLogger(__name__)


def fetch_env_snapshot_from_open_meteo(latitude: float,longitude: float) -> Dict[str, Any]:
  """Fetches environmental snapshot from Open-Meteo API"""
  start_time = time.time()
  
  observability.log_tool_call("fetch_env_snapshot_from_open_meteo", {"latitude": latitude,"longitude": longitude})
  
  if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
    error = ValueError(f"Coordinates must be numeric: lat={latitude}, lon={longitude}")
    observability.log_error("fetch_env_snapshot_from_open_meteo", error)
    raise error
  
  if not (-90 <= latitude <= 90):
    error = ValueError(f"Invalid latitude: {latitude} (must be -90 to 90)")
    observability.log_error("fetch_env_snapshot_from_open_meteo", error)
    raise error
  
  if not (-180 <= longitude <= 180):
    error = ValueError(f"Invalid longitude: {longitude} (must be -180 to 180)")
    observability.log_error("fetch_env_snapshot_from_open_meteo", error)
    raise error
  
  base_url = "https://api.open-meteo.com/v1/forecast"
  params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": [
      "temperature_2m",
      "apparent_temperature",
      "relative_humidity_2m",
      "wind_speed_10m"
    ],
    "hourly": ["pm10", "pm2_5"],
    "timezone": "auto"
  }
  
  try:
    logger.debug(f"Calling Open-Meteo API for ({latitude}, {longitude}) | ")
    resp = requests.get(base_url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    current = data.get("current", {})
    hourly = data.get("hourly", {})
    
    snapshot = {
      "location": {
        "latitude": latitude,
        "longitude": longitude
      },
      "current": {
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "relative_humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_10m_ms": current.get("wind_speed_10m")
      },
      "hourly": {
        "pm10": hourly.get("pm10"),
        "pm2_5": hourly.get("pm2_5")
      },
      "raw": data
    }

    duration_ms = (time.time() - start_time) * 1000
    observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=True,duration_ms=duration_ms)
    
    logger.info(f"Successfully fetched snapshot for ({latitude}, {longitude}) | ")
    
    return snapshot
  
  except requests.Timeout as e:
    duration_ms = (time.time() - start_time) * 1000
    observability.log_error("fetch_env_snapshot_from_open_meteo",e,details=f"Timeout after {duration_ms:.0f}ms")
    observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except requests.HTTPError as e:
    duration_ms = (time.time() - start_time) * 1000
    observability.log_error("fetch_env_snapshot_from_open_meteo",e,details=f"HTTP {resp.status_code}: {resp.text[:200]}")
    observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except requests.RequestException as e:
    duration_ms = (time.time() - start_time) * 1000
    observability.log_error("fetch_env_snapshot_from_open_meteo",e,details="Request failed")
    observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except Exception as e:
    duration_ms = (time.time() - start_time) * 1000
    observability.log_error("fetch_env_snapshot_from_open_meteo",e,details="Unexpected error during API call")
    observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise


def geocode_place_name(place_name: str,max_results: int = 3) -> Dict[str, Any]:
  """Geocodes a place name to coordinates using Open-Meteo Geocoding API."""
  start_time = time.time()
  
  observability.log_tool_call("geocode_place_name", {"place_name": place_name,"max_results": max_results})
  
  url = "https://geocoding-api.open-meteo.com/v1/search"
  
  def _call_api(name: str) -> Dict[str, Any]:
    try:
      logger.debug(f"Geocoding: '{name}'")
      resp = requests.get(
        url,
        params={
          "name": name,
          "count": max_results,
          "language": "en",
          "format": "json"
        },
        timeout=20
      )
      resp.raise_for_status()
      data = resp.json()
      return {"ok": True, "data": data}
    
    except requests.Timeout:
      return {
        "ok": False,
        "error": "timeout",
        "message": f"Timeout contacting Open-Meteo geocoding for '{name}' | "
      }
    except requests.RequestException as e:
      return {
        "ok": False,
        "error": "request_failed",
        "message": f"Request error ({type(e).__name__}) for '{name}' | "
      }

  cleaned = place_name.strip()
  candidates: list[str] = [cleaned]
  
  parts = [p.strip() for p in cleaned.split(",") if p.strip()]
  if len(parts) >= 2:
    candidates.append(", ".join(parts[:2]))
  if len(parts) >= 1:
    candidates.append(parts[0])
  
  seen = set()
  unique_candidates: list[str] = []
  for c in candidates:
    if c not in seen:
      seen.add(c)
      unique_candidates.append(c)
  
  logger.debug(f"Geocoding candidates: {unique_candidates} | ")
  
  last_error: Dict[str, Any] | None = None
  
  for candidate in unique_candidates:
    api_result = _call_api(candidate)
    
    if not api_result.get("ok"):
      last_error = api_result
      continue
    
    data = cast(Dict[str, Any], api_result["data"])
    raw_results: List[Dict[str, Any]] = data.get("results") or []
    results: List[Dict[str, Any]] = []
    
    for r in raw_results:
      results.append({
        "name": r.get("name"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "country": r.get("country"),
        "admin1": r.get("admin1")
      })
    
    if results:
      duration_ms = (time.time() - start_time) * 1000
      observability.log_tool_complete(
        "geocode_place_name",
        success=True,
        duration_ms=duration_ms
      )
      
      logger.info(
        f"Geocoded '{candidate}' into {len(results)} result(s) | "
        f"in {duration_ms:.0f}ms"
      )
      
      return {
        "query": candidate,
        "results": results
      }

  duration_ms = (time.time() - start_time) * 1000
  
  out: Dict[str, Any] = {
    "query": place_name,
    "results": []
  }
  
  if last_error is not None:
    out["error"] = last_error.get("error")
    out["error_message"] = last_error.get("message")
    logger.warning(
      f"⚠️ Geocoding failed for '{place_name}': {last_error.get('message')}"
    )
  else:
    logger.warning(f"⚠️ No geocoding results found for '{place_name}'")
  
  observability.log_tool_complete(
    "geocode_place_name",
    success=False,
    duration_ms=duration_ms
  )
  
  return out