# Theophrastus - The Weather & Environmental Advisor Agent

![Architecture](./Theophrastus_thumbnail.png "Theophrastus_thumbnail")

## Overview 

Theophrastus is a multi-agent system that provides comprehensive environmental weather analysis and outdoor activity recommendations. Named after Theophrastus of Eresos-the ancient Greek philosopher known as the "Father of Botany," successor to Aristotle, and pioneer of meteorology. This intelligent agent combines real-time meteorological data with advanced risk assessment to help users make informed decisions about outdoor activities and agricultural planning.

In this system, Theophrastus serves as the central orchestrator, a prophet-philosopher who communes with a divine council of elemental deities to interpret weather patterns and provide sage counsel. Zephyr brings wind and weather data, Atlas maps the terrain, Aether assesses atmospheric dangers, Aurora illuminates the path forward with clear guidance and Phosphoros ensures the dawn of wisdom always arrives. Through this divine communion, Theophrastus interprets celestial signs and atmospheric omens, transforming raw environmental data into actionable wisdom.

True to his historical namesake who authored foundational works on plant classification, meteorology, and the intricate relationships between flora and their environment, Theophrastus offers guidance not only for outdoor recreation but for agricultural endeavors—advising on optimal planting and harvest timing and the delicate balance between humanity's needs and nature's rhythms. Like the ancient philosopher who studied how plants respond to seasons and weather, this agent bridges the gap between environmental science and practical wisdom, helping farmers and outdoor enthusiasts work in harmony with the natural world. 

## Problem Statement

Planning outdoor activities requires synthesizing complex environmental data from multiple sources - temperature, wind conditions, humidity, precipitation, and location-specific factors. Manual analysis of these variables is:

- Time-Consuming: Gathering data from multiple weather sources and cross-referencing conditions takes significant effort.
Error-Prone: Missing critical risk factors can lead to unsafe decisions.
- Location-Limited: Finding optimal locations for specific activities requires local knowledge that may not be readily available.
- Context-Lacking: Raw weather data doesn't translate directly into actionable advice for specific activities.

Users need a system that not only fetches environmental data but intelligently interprets it, assesses risks, and provides personalized recommendations based on their planned activities and locations.

### Key Features

- Real-Time Weather Data: Fetches current conditions and forecasts from Open-Meteo API.
- Location Discovery: Finds optimal locations based on activity types.
- Risk Assessment: Analyzes environmental hazards.
- Reports: Generates recommendations.
- Quality Assurance: Built-in validation and evaluation.
- Monitoring: Observability with metrics and traces.

### Functionality Example

```
USER: "I want to go hiking near Mexico City this weekend"

Theophrastus WorkFlow:
 *FIRST: Searches for hiking locations.
 *THEN: Fetches weather for each location.
 *THEN: Assesses environmental risks.
 *FINALLY: Generates personalized recommendations.

RESULT: Complete hiking guide with safety analysis and location comparisons!
```

## Use Cases

### Outdoor Recreation:
- Hiking and trekking.
- Cycling routes.
- Camping locations.

### Event Planning:
- Festivals.
- Concerts.
- Sport events.

### Professional Applications:
- Construction planning.
- Agricultural scheduling.
- Field activities.

### Travel Planning:
- Destination weather.
- Beach conditions.

## Architecture

Theophrastus employs a **multi-agent orchestration system** where agents and tools collaborate:

![Architecture](./TheoprhastusArchitecture.png "Theophrastus_Architecture")

### The Sub Agents

#### Zephyr (Data Agent)
- Fetches weather data from Open-Meteo API.
- Processes current conditions and forecasts.
- Validates data completeness.

_Named after Zephyros, Greek god of the west wind—the gentle spring breeze that brings favorable weather and seasonal change._

#### Atlas (Location Agent)  
- Discovers locations based on activity.
- Geocodes and validates coordinates.
- Enriches with geographic metadata.

_Named after the Titan Atlas, condemned to hold up the celestial spheres—now known as the bearer of maps and geographic knowledge._

#### Aether (Risk Agent)
- Assesses temperature extremes.
- Evaluates wind dangers.
- Analyzes precipitation risks.

_Named after Aether, primordial deity of the upper air—the pure, bright atmosphere the gods breathe, distinct from the mortal air below._

#### Aurora (Advice Writer)
- Synthesizes all gathered data.
- Generates professional markdown reports.
- Provides actionable recommendations.

_Named after Aurora (Eos in Greek), goddess of dawn—who brings light and clarity each morning, illuminating the path forward._

### Phosphoros (Aurora Herald)
- Monitors workflow state after risk assessment completion.
- Enforces Aurora execution when risk data exists without advice.
- Prevents workflow short-circuits by ensuring complete recommendations.

_Named after the Greek god who heralds Aurora's arrival as the morning star._

## Quick Start

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd weather_advisor_agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running Theophrastus

- Option 1: ADK Web Interface (Recommended)
```bash
adk web
# Navigate to `http://localhost:8000`
```


- Option 2: Python Script
```bash
python -m test.test_agent_logger_on
```

### Usage Example

```python
# Simple weather query
"How is the weather in Sacramento, California?"

# Location discovery
"Find good hiking spots near Mexico City"

# Activity planning  
"I want to go cycling this weekend. Where should I go?"

# Full analysis
"What's the weather like for hiking in those locations?"
```

## Project Structure

```
weather_advisor_agent/
    -sub_agents/
        -zephyr_env_data_agent.py       # Weather data collection
        -atlas_env_location_agent.py    # Location discovery
        -aether_env_risk_agent.py       # Risk assessment
        -aurora_env_advice_writer.py    # Advice generation
    -tools/
        -web_access_tools.py            # API integrations
        -creation_tools.py              # File utilities
        -func_tools.py                  # Helper functions
    -utils/
        -observability.py               # Logging & metrics
        -agent_utils.py                 # Agent utilities
    -evaluation/
        -evaluator.py                   # Evaluation engine
        -eval_integration.py            # Integration helpers
        -README.md                      # Evaluation docs
    -memory/
        -memory_bank.py                 # Session memory
    -data/
        -envi_memory.json               # Memory bank
    -evaluations/                       # Evaluation reports
        -*.json                         # Metrics & traces
    - test/
        -test_agent_logger_on.py        # Integration tests
        -test_agent_with_evaluation.py  # Evaluation tests
    -Theophrastus_root_agent.py         # Main orchestrator
    -validation_checkers.py             # Quality validation
    -config.py                          # Configuration
    -requirements.txt                   # Dependencies
    -README.md                          # This file
```

## Features in Detail

### 1. Multi-Location Analysis
Compare weather across multiple locations to find the best option:
```
User: "Compare hiking conditions in these three locations"
→ Fetches data for all locations
→ Assesses risks individually  
→ Recommends optimal choice
```

### 2. Risk-Based Recommendations
Recommendations based on risks:
- Heat Risk: Temperature and apparent temperature analysis
- Cold Risk: Hypothermia and exposure evaluation
- Wind Risk: Dangerous wind speed detection
- Overall Risk: Composite safety rating

### 3. Professional Reports
Structured markdown output with:
- Executive summary
- Current conditions
- Detailed recommendations
- Risk assessment
- Timing suggestions

### 4. Quality Assurance

Validation System:
- Data completeness checks
- Coordinate validation
- Risk report structure
- Advice quality assessment

Evaluation System:
- Quality categories
- Automated scoring
- Performance monitoring
- JSON export for analysis

### 5. Observability

Full instrumentation with:
- Structured logging
- Performance metrics
- Operation tracing
- Error tracking
- JSON exports

## Testing

### How To Run Integrated Tests
```bash
# Basic test
python -m test.test_agent_logger_on

# With evaluation
python -m test.test_agent_with_evaluation
```

### Test Coverage
- Data collection.
- Location discovery.
- Risk assessment.
- Advice generation.
- Validation system.
- Evaluation metrics.

## Configuration

### .env Variables

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional  
LOG_LEVEL=INFO
EVALUATION_ENABLED=true
```

### Model .config

Edit `config.py` to customize models:
```python
root_model = "gemini-2.5-flash"
worker_model = "gemini-2.5-flash"
risk_model = "gemini-2.5-pro"
mapper_model = "gemini-2.0-flash-lite"
data_model = "gemini-2.0-flash-lite"
```

## API Integration for Tools

### Open-Meteo Weather API
- Endpoint: `https://api.open-meteo.com/v1/forecast`.
- Authentication: No requierements (free tier).
- Data: Temperature, wind, humidity, precipitation.
- Coverage: Global.
- Resolution: Hourly forecasts.

## Troubleshooting

### Common Issues

Issue: "No API key found"  
Solution: Ensure `GOOGLE_API_KEY` is set in `.env`.

Issue: "Response time too slow"  
Solution: Check network connectivity and API rate limits.

Issue: "Resource exhausted"  
Solution: Check API quota for RPM(Responses Per Minute) and TPM(Tokens Per Minute).

## Future Ideas To Integrate!

### Version 2.0
- [ ] Historical weather analysis.
- [ ] Extended forecasts (7-14 days).

### Version 3.0
- [ ] Multi-provider weather aggregation.
- [ ] Built-in machine learning models.

## License

Apache License - see [LICENSE](LICENSE) file for details.

## Contributions & Support!
If you want to contribute for the development, thank you so much!
So please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

If you find Theophrastus useful, please star the repository!