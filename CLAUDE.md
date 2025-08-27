# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Currency Converter REST API service built for Shell Trading assessment. Provides real-time currency conversion using Binance Bitcoin prices as the exchange rate source.

## Architecture

### Core Components
- **FastAPI Application** (`main.py`) - ASGI web server with OpenAPI documentation
- **Services Layer** (`app/services/`) - Business logic for Binance API integration and FX calculations  
- **Models** (`app/models/`) - Pydantic data models for request/response validation
- **Utils** (`app/utils/`) - Caching and utility functions

### Key Design Patterns
- **Service Layer Pattern** - Separates API logic from business logic
- **Dependency Injection** - FastAPI's built-in DI for services
- **Async/Await** - Non-blocking I/O for external API calls
- **Caching Strategy** - Hourly rate updates with fallback mechanisms

## Development Commands

### Setup and Dependencies
```bash
# Verify Python version (3.11+ required)
python3 --version

# Install dependencies
pip3 install -r requirements.txt

# Or with development dependencies
pip3 install -e .[test]

# Recommended: Use virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server with hot reload
python3 main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_binance_service.py

# Run with verbose output
pytest -v
```

### Docker Operations
```bash
# Build image
docker build -t currency-converter .

# Run container
docker run -p 8000:8000 currency-converter

# Run with docker-compose (includes Redis)
docker-compose up --build
```

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Convert currency
curl "http://localhost:8000/convert?ccy_from=USD&ccy_to=GBP&quantity=1000"

# API documentation
curl http://localhost:8000/docs
```

## FX Rate Calculation Logic

The service derives exchange rates using Bitcoin as an intermediary:
- Direct rates: USD/GBP = BTCUSD / BTCGBP
- Inverse rates: GBP/USD = BTCGBP / BTCUSD
- Same currency: Returns original amount

Supported currency pairs are determined by available Binance BTC trading pairs (BTCUSD, BTCEUR, BTCGBP, etc.).

## Caching Strategy

- **Rate Updates**: Fetched hourly from Binance API
- **Cache Storage**: In-memory with Redis fallback option
- **Cache Keys**: `btc_rates:{timestamp}` format
- **TTL**: 3600 seconds (1 hour)

## Error Handling

- **400 Bad Request**: Invalid currency codes or negative amounts
- **500 Internal Server Error**: Binance API failures or calculation errors
- **Rate Limiting**: Built-in FastAPI middleware protection

## Production Considerations

- Environment variables for configuration (REDIS_URL, LOG_LEVEL)
- Structured JSON logging for observability
- Health check endpoint for load balancer probes
- Docker containerization with multi-stage builds
- Async HTTP client with connection pooling