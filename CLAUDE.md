# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Secure, enterprise-grade Currency Converter REST API service built for Shell Trading assessment. Provides real-time currency conversion using Binance Bitcoin prices with comprehensive security scanning, CI/CD automation, and Kubernetes-native deployment.

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

## CI/CD Pipeline

### GitHub Actions Workflows
The project includes three comprehensive workflows:

1. **CI Pipeline** (`ci.yml`) - Runs on every push/PR
   - Code quality (Ruff, Black, isort, Bandit)
   - Testing with coverage (pytest, 80% threshold)
   - Security scanning (Safety, Trivy, Hadolint)
   - Helm validation and integration tests

2. **Security Pipeline** (`security.yml`) - Weekly + PR scans
   - SonarQube static analysis
   - OWASP dependency checking
   - Secret detection (GitLeaks, TruffleHog)
   - Container security (Trivy, Grype, SBOM)
   - Compliance scanning (license, OPA policies)

3. **Release Pipeline** (`release.yml`) - Tag-triggered deployment
   - Pre-release security validation
   - Multi-arch container builds with signing
   - Automated staging/production deployment
   - Health check validation

### Security Tools Configuration
- `sonar-project.properties` - SonarQube settings
- `.bandit` - Python security scanner config
- `dependency-check-suppressions.xml` - OWASP suppressions
- `security-policies/` - OPA Conftest policies
- `requirements-dev.txt` - Dev and security dependencies

### Development Commands
```bash
# Install security tools
pip install -r requirements-dev.txt

# Run security checks locally
bandit -r app/
safety check
ruff check .

# Full validation before PR
./scripts/validate-helm.sh
pytest --cov=app tests/
black --check .
```

## Security Architecture

This project implements enterprise-grade security with multiple layers of protection:

### Security Tools Integration
- **Bandit**: Python code security scanning with custom configuration
- **Safety**: Dependency vulnerability monitoring
- **Trivy**: Container image and filesystem vulnerability scanning
- **SonarQube**: Comprehensive code quality and security analysis
- **OWASP Dependency Check**: Known vulnerability database matching
- **GitLeaks + TruffleHog**: Secret detection across commit history
- **Hadolint**: Dockerfile security and best practices
- **OPA Conftest**: Policy-as-code security validation
- **Kubesec**: Kubernetes security assessment
- **Cosign**: Container image cryptographic signing

### Security Quality Gates
- **PR Requirements**: No high-severity vulnerabilities allowed
- **Release Blocking**: Critical security issues prevent deployments
- **Weekly Scanning**: Proactive vulnerability monitoring
- **SBOM Generation**: Complete software bill of materials
- **Image Signing**: Supply chain integrity verification

### Container Security Hardening
- Non-root user execution (UID 1000)
- Read-only root filesystem
- Dropped capabilities (ALL removed)
- Security contexts enforced
- Distroless base images
- Multi-architecture support

### Local Security Development
```bash
# Security development workflow
pip install -r requirements-dev.txt
bandit -r app/ -ll
safety check
trivy fs .
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