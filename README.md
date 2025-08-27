# Currency Converter API

A real-time currency conversion REST API service that uses Binance Bitcoin prices to derive exchange rates. Built for Shell Trading assessment.

## Features

- **Real-time Exchange Rates**: Uses Binance BTC prices to calculate currency conversion rates
- **REST API**: Simple GET endpoint with query parameters
- **Caching**: Hourly rate updates with in-memory caching for performance
- **Production Ready**: Docker containerization, health checks, and comprehensive error handling
- **Well Tested**: Full test coverage with unit and integration tests

## API Usage

### Convert Currency

**Endpoint:** `GET /convert`

**Parameters:**
- `ccy_from` - Source currency code (e.g., USD, EUR, GBP)
- `ccy_to` - Target currency code (e.g., USD, EUR, GBP)  
- `quantity` - Amount to convert (must be > 0)

**Examples:**

1. **USD to GBP conversion:**
```bash
curl "http://localhost:8000/convert?ccy_from=USD&ccy_to=GBP&quantity=1000"
```
Response:
```json
{"quantity": 3102.59, "ccy": "GBP"}
```

2. **GBP to EUR conversion:**
```bash
curl "http://localhost:8000/convert?ccy_from=GBP&ccy_to=EUR&quantity=500"
```
Response:
```json
{"quantity": 187.0, "ccy": "EUR"}
```

3. **Same currency (no conversion):**
```bash
curl "http://localhost:8000/convert?ccy_from=USD&ccy_to=USD&quantity=1000"
```
Response:
```json
{"quantity": 1000.0, "ccy": "USD"}
```

4. **EUR to USD conversion:**
```bash
curl "http://localhost:8000/convert?ccy_from=EUR&ccy_to=USD&quantity=100"
```
Response:
```json
{"quantity": 107.25, "ccy": "USD"}
```

### Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "service": "currency-converter"
}
```

### Error Responses

**Invalid currency:**
```bash
curl "http://localhost:8000/convert?ccy_from=XYZ&ccy_to=GBP&quantity=1000"
```
Response:
```json
{"detail": "Currency XYZ not supported"}
```

**Negative amount:**
```bash
curl "http://localhost:8000/convert?ccy_from=USD&ccy_to=GBP&quantity=-100"
```
Response:
```json
{"detail": [{"type": "greater_than", "loc": ["query", "quantity"], "msg": "Input should be greater than 0"}]}
```

## Supported Currencies

The service supports currencies that have BTC trading pairs on Binance:
- USD, EUR, GBP, JPY
- AUD, CAD, CHF, SEK, NOK, DKK
- PLN, ZAR

## Requirements

- Python 3.11+ (required)
- pip (Python package manager)

## Quick Start

### Local Development

1. **Verify Python version:**
```bash
python3 --version  # Should show Python 3.11 or higher
# If python3 is not found, try: python --version
```

2. **Install dependencies:**
```bash
# Option 1: Using requirements.txt
pip3 install -r requirements.txt

# Option 2: Using pyproject.toml (recommended for clean environments)
pip3 install -e .

# Option 3: Create virtual environment first (recommended)
python3 -m venv currency-converter-env
source currency-converter-env/bin/activate  # On Windows: currency-converter-env\Scripts\activate
pip install -r requirements.txt  # pip (not pip3) inside activated venv
```

3. **Run the service:**
```bash
python3 main.py
# Or inside activated virtual environment: python main.py
```

4. **Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker

1. **Build and run:**
```bash
docker build -t currency-converter .
docker run -p 8000:8000 currency-converter
```

2. **With Docker Compose (includes Redis):**
```bash
docker-compose up --build
```

### Kubernetes Deployment

Deploy to Kubernetes using the included Helm chart:

1. **Build and push Docker image:**
```bash
# Build the image
docker build -t currency-converter:v1.0.0 .

# Tag for your registry
docker tag currency-converter:v1.0.0 your-registry/currency-converter:v1.0.0

# Push to registry
docker push your-registry/currency-converter:v1.0.0
```

2. **Deploy with Helm:**

**Basic deployment:**
```bash
helm install currency-converter helm/currency-converter/ \
  --set image.repository=your-registry/currency-converter \
  --set image.tag=v1.0.0
```

**Development deployment:**
```bash
helm install currency-converter-dev helm/currency-converter/ \
  -f helm/currency-converter/values-development.yaml \
  --set image.repository=your-registry/currency-converter
```

**Production deployment:**
```bash
helm install currency-converter-prod helm/currency-converter/ \
  -f helm/currency-converter/values-production.yaml \
  --set image.repository=your-registry/currency-converter \
  --set image.tag=v1.0.0
```

**Custom deployment with specific settings:**
```bash
helm install currency-converter helm/currency-converter/ \
  --set image.repository=your-registry/currency-converter \
  --set image.tag=v1.0.0 \
  --set replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.company.com \
  --set autoscaling.enabled=true \
  --set redis.enabled=true \
  --set redis.host=redis-service
```

3. **Access the service:**
```bash
# Port forward for testing
kubectl port-forward svc/currency-converter 8080:80

# Test the API
curl http://localhost:8080/health
curl "http://localhost:8080/convert?ccy_from=USD&ccy_to=GBP&quantity=1000"
```

4. **Validate and test the Helm chart:**
```bash
# Lint the chart
helm lint helm/currency-converter/

# Test template rendering
helm template test-release helm/currency-converter/ --dry-run

# Test with production values
helm template prod-test helm/currency-converter/ \
  -f helm/currency-converter/values-production.yaml

# Upgrade deployment
helm upgrade currency-converter helm/currency-converter/ \
  --set image.tag=v1.1.0
```

5. **Monitor the deployment:**
```bash
# Check pods
kubectl get pods -l app.kubernetes.io/name=currency-converter

# View logs
kubectl logs -l app.kubernetes.io/name=currency-converter

# Check service
kubectl get svc currency-converter

# Check HPA (if enabled)
kubectl get hpa currency-converter

# Check ingress (if enabled)
kubectl get ingress currency-converter
```

**Helm Chart Features:**
- **Multi-environment support**: Development, staging, and production value files
- **Auto-scaling**: Horizontal Pod Autoscaler with CPU/memory metrics
- **Security**: Security contexts, RBAC, non-root containers
- **Observability**: Health checks, liveness/readiness probes, monitoring hooks
- **Flexibility**: Configurable ingress, services, resources, and Redis integration
- **Production-ready**: TLS termination, resource limits, pod disruption budgets

See `helm/currency-converter/README.md` for detailed Helm chart configuration options and examples.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_api.py -v
```

## Architecture

### Exchange Rate Calculation

The service uses Bitcoin as an intermediary currency to calculate exchange rates:

```
EUR/USD = BTCEUR / BTCUSD
```

For example:
- BTCUSD = 45,000 (1 BTC = 45,000 USD)
- BTCEUR = 37,500 (1 BTC = 37,500 EUR)  
- EUR/USD = 45,000 / 37,500 = 1.20

### Components

- **FastAPI Application** (`main.py`) - Web server and API endpoints
- **Binance Service** (`app/services/binance_service.py`) - Fetches BTC prices from Binance API
- **FX Service** (`app/services/fx_service.py`) - Calculates exchange rates and conversions
- **Cache Manager** (`app/utils/cache.py`) - Handles rate caching with TTL
- **Models** (`app/models/`) - Pydantic models for request/response validation

### Caching Strategy

- **Rate Updates**: Fetched hourly from Binance API (configurable)
- **Fallback**: Uses cached rates if API is unavailable
- **Performance**: Reduces API calls and improves response times

## Configuration

Environment variables (optional):
```bash
LOG_LEVEL=info          # Logging level
REDIS_URL=redis://localhost:6379  # Redis URL (if using Redis cache)
CACHE_TTL=3600         # Cache TTL in seconds
BINANCE_API_TIMEOUT=30 # API timeout in seconds
```

## Production Deployment

The service is designed for production deployment with:

- **Containerization**: Docker and Docker Compose
- **Kubernetes Ready**: Complete Helm chart for K8s deployment
- **Health Checks**: `/health` endpoint for load balancers and probes
- **Auto-scaling**: Horizontal Pod Autoscaler support
- **Security**: Non-root containers, security contexts, RBAC
- **Error Handling**: Proper HTTP status codes and error messages
- **Logging**: Structured logging for monitoring
- **Performance**: Async operations and connection pooling

## API Documentation

Interactive API documentation is available at `/docs` when running the service.

## License

Built for Shell Trading assessment.