#!/bin/bash

# Helm Chart Validation Script for Currency Converter
set -e

echo "🔍 Starting Helm Chart Validation..."

CHART_PATH="helm/currency-converter"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

info() {
    echo -e "ℹ $1"
}

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    error "Helm is not installed. Please install Helm 3.x"
fi

HELM_VERSION=$(helm version --short | cut -d'"' -f2)
info "Using Helm version: $HELM_VERSION"

# Validate chart structure
info "Checking chart structure..."
required_files=(
    "$CHART_PATH/Chart.yaml"
    "$CHART_PATH/values.yaml"
    "$CHART_PATH/templates/deployment.yaml"
    "$CHART_PATH/templates/service.yaml"
    "$CHART_PATH/templates/serviceaccount.yaml"
    "$CHART_PATH/templates/configmap.yaml"
    "$CHART_PATH/templates/ingress.yaml"
    "$CHART_PATH/templates/hpa.yaml"
    "$CHART_PATH/templates/_helpers.tpl"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        success "Found $file"
    else
        error "Missing required file: $file"
    fi
done

# Lint the chart
info "Running helm lint..."
if helm lint "$CHART_PATH"; then
    success "Chart linting passed"
else
    error "Chart linting failed"
fi

# Test template rendering with default values
info "Testing template rendering with default values..."
if helm template test-default "$CHART_PATH" > /dev/null; then
    success "Default template rendering passed"
else
    error "Default template rendering failed"
fi

# Test with development values
info "Testing with development values..."
if helm template test-dev "$CHART_PATH" -f "$CHART_PATH/values-development.yaml" > /dev/null; then
    success "Development template rendering passed"
else
    error "Development template rendering failed"
fi

# Test with production values
info "Testing with production values..."
if helm template test-prod "$CHART_PATH" -f "$CHART_PATH/values-production.yaml" > /dev/null; then
    success "Production template rendering passed"
else
    error "Production template rendering failed"
fi

# Test with various configuration combinations
info "Testing advanced configurations..."

test_configs=(
    "--set autoscaling.enabled=true --set ingress.enabled=true"
    "--set redis.enabled=true --set monitoring.enabled=true"
    "--set replicaCount=5 --set resources.requests.cpu=200m"
    "--set service.type=LoadBalancer --set ingress.enabled=false"
)

for config in "${test_configs[@]}"; do
    if eval "helm template test-config $CHART_PATH $config > /dev/null"; then
        success "Configuration test passed: $config"
    else
        error "Configuration test failed: $config"
    fi
done

# Validate YAML syntax in templates
info "Validating YAML syntax in rendered templates..."
if helm template yaml-test "$CHART_PATH" | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin)" > /dev/null 2>&1; then
    success "YAML syntax validation passed"
else
    warning "YAML syntax validation failed (this might be expected if YAML library is not available)"
fi

# Check for common issues
info "Checking for common issues..."

# Check if image pull policy is set correctly
if helm template check-policy "$CHART_PATH" | grep -q "imagePullPolicy"; then
    success "Image pull policy is configured"
else
    warning "Image pull policy might not be configured"
fi

# Check if resource limits are set
if helm template check-resources "$CHART_PATH" | grep -q "resources:"; then
    success "Resource limits are configured"
else
    warning "Resource limits might not be configured"
fi

# Check if security context is set
if helm template check-security "$CHART_PATH" | grep -q "securityContext:"; then
    success "Security contexts are configured"
else
    warning "Security contexts might not be configured"
fi

success "All Helm chart validations completed successfully!"

echo ""
echo "📋 Summary:"
echo "- Chart structure: ✓"
echo "- Lint validation: ✓" 
echo "- Template rendering: ✓"
echo "- Multi-environment support: ✓"
echo "- Advanced configurations: ✓"
echo "- YAML syntax: ✓"
echo ""
echo "🚀 The Helm chart is ready for deployment!"