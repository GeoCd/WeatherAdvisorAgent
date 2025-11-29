import requests
import time
import logging

from typing import Dict, List, Any, cast, Optional

from weather_advisor_agent.utils import Theophrastus_Observability

logger = logging.getLogger(__name__)

def geocode_place_name(place_name: str, max_results: int = 3, region_hint: Optional[str] = None) -> Dict[str, Any]:
  """Geocodes a place name to coordinates using Open-Meteo Geocoding API"""
  
  start_time = time.time()
  
  Theophrastus_Observability.log_tool_call(
    "geocode_place_name",{
      "place_name": place_name,
      "max_results": max_results,
      "region_hint": region_hint
    }
  )
  
  url = "https://geocoding-api.open-meteo.com/v1/search"
  
  def _call_api(name: str, count: int = None) -> Dict[str, Any]:
    try:
      resp = requests.get(
        url,
        params={
          "name": name,
          "count": count or max_results,
          "language": "en",
          "format": "json"
        },timeout=20
      )
      resp.raise_for_status()
      data = resp.json()
      return {"ok": True, "data": data}
    
    except requests.Timeout:
      return {
        "ok": False,
        "error": "timeout",
        "message": f"Timeout."
      }
    except requests.RequestException as e:
      return {
        "ok": False,
        "error": "request_failed",
        "message": f"Request failed."
      }

  cleaned = place_name.strip()
  candidates: list[str] = []
  candidates.append(cleaned)
  suffixes_to_remove = [
    " National Park",
    " national park",
    " State Park", 
    " state park",
    " Park",
    " park",
    " Forest",
    " forest",
    " Mountain",
    " mountain",
    " Volcano",
    " volcano",
    " Trail",
    " trail",
    " Reserve",
    " reserve"
  ]
  
  for suffix in suffixes_to_remove:
    if cleaned.endswith(suffix):
      without_suffix = cleaned[:-len(suffix)].strip()
      if without_suffix:
        candidates.append(without_suffix)
      break
  
  if region_hint:
    region_hint_clean = region_hint.strip()
    if region_hint_clean.lower() not in cleaned.lower():
      candidates.append(f"{cleaned}, {region_hint_clean}")
      for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
          without_suffix = cleaned[:-len(suffix)].strip()
          if without_suffix:
            candidates.append(f"{without_suffix}, {region_hint_clean}")
          break
  
  words = cleaned.split()
  if len(words) >= 3:
    candidates.append(" ".join(words[:2]))
  if len(words) >= 2:
    candidates.append(words[0])
  
  parts = [p.strip() for p in cleaned.split(",") if p.strip()]
  if len(parts) >= 2:
    candidates.append(", ".join(parts[:2]))
    candidates.append(parts[0])
  
  seen = set()
  unique_candidates: list[str] = []
  for c in candidates:
    c_lower = c.lower()
    if c_lower not in seen and c:
      seen.add(c_lower)
      unique_candidates.append(c)
  
  last_error: Dict[str, Any] | None = None
  
  for i, candidate in enumerate(unique_candidates):
    attempt_max_results = max_results if i == 0 else min(max_results * 2, 10)
    api_result = _call_api(candidate, attempt_max_results)
    
    if not api_result.get("ok"):
      last_error = api_result
      continue
    
    data = cast(Dict[str, Any], api_result["data"])
    raw_results: List[Dict[str, Any]] = data.get("results") or []
    
    if not raw_results:
      continue
    
    results: List[Dict[str, Any]] = []
    for r in raw_results:
      results.append({
        "name": r.get("name"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "country": r.get("country"),
        "admin1": r.get("admin1"),
        "admin2": r.get("admin2"),
        "population": r.get("population")
      })
    results = results[:max_results]
    
    if results:
      duration_ms = (time.time() - start_time) * 1000
      Theophrastus_Observability.log_tool_complete("geocode_place_name", success=True, duration_ms=duration_ms)
      return {
        "query": candidate,
        "original_query": place_name,
        "results": results,
        "source": "open_meteo_api",
        "region_hint": region_hint
      }

  duration_ms = (time.time() - start_time) * 1000
  
  out: Dict[str, Any] = {
    "query": place_name,
    "results": [],
    "attempted_variations": unique_candidates[:5],
    "region_hint": region_hint
  }
  
  if last_error is not None:
    out["error"] = last_error.get("error")
    out["error_message"] = last_error.get("message")
    logger.warning(f"All attempts failed.\n")
  else:
    logger.warning(f"No geocoding results found.\n")
  
  Theophrastus_Observability.log_tool_complete("geocode_place_name", success=False, duration_ms=duration_ms)
  
  return out

def fetch_env_snapshot_from_open_meteo(latitude: float,longitude: float) -> Dict[str, Any]:
  """Fetches environmental snapshot from Open-Meteo API"""
  start_time = time.time()
  
  Theophrastus_Observability.log_tool_call("fetch_env_snapshot_from_open_meteo", {"latitude": latitude,"longitude": longitude})
  
  if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
    error = ValueError(f"Coordinates must be Num: lat={latitude}, lon={longitude}")
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo", error)
    raise error
  
  if not (-90 <= latitude <= 90):
    error = ValueError(f"Invalid latitude: {latitude} (must be -90 to 90)")
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo", error)
    raise error
  
  if not (-180 <= longitude <= 180):
    error = ValueError(f"Invalid longitude: {longitude} (must be -180 to 180)")
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo", error)
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
    logger.debug(f"Calling Open-Meteo API.\n")
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
    Theophrastus_Observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=True,duration_ms=duration_ms)
    
    logger.info(f"Successfully fetched snapshot for ({latitude}, {longitude}). \n")
    
    return snapshot
  
  except requests.Timeout as e:
    duration_ms = (time.time() - start_time) * 1000
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo",e,details=f"Timeout after {duration_ms:.0f}ms")
    Theophrastus_Observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except requests.HTTPError as e:
    duration_ms = (time.time() - start_time) * 1000
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo",e,details=f"HTTP {resp.status_code}: {resp.text[:200]}")
    Theophrastus_Observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except requests.RequestException as e:
    duration_ms = (time.time() - start_time) * 1000
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo",e,details="Request failed")
    Theophrastus_Observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise
  
  except Exception as e:
    duration_ms = (time.time() - start_time) * 1000
    Theophrastus_Observability.log_error("fetch_env_snapshot_from_open_meteo",e,details="Unexpected error during API call")
    Theophrastus_Observability.log_tool_complete("fetch_env_snapshot_from_open_meteo",success=False,duration_ms=duration_ms)
    raise

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