# Currency Converter Helm Chart

This Helm chart deploys the Currency Converter API on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+

## Installation

### Add Repository (if using a Helm repository)
```bash
helm repo add shell-trading https://charts.shelltrading.com
helm repo update
```

### Install from Local Chart
```bash
# From the project root directory
helm install currency-converter helm/currency-converter/

# With custom values
helm install currency-converter helm/currency-converter/ \
  --set replicaCount=3 \
  --set image.tag=v1.0.0
```

### Install with Custom Values File
```bash
helm install currency-converter helm/currency-converter/ -f custom-values.yaml
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `currency-converter` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `ingress.enabled` | Enable ingress | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `config.logLevel` | Application log level | `info` |
| `redis.enabled` | Enable Redis | `false` |

## Examples

### Basic Installation
```bash
helm install my-currency-converter helm/currency-converter/
```

### Production Installation with Ingress
```bash
helm install currency-converter helm/currency-converter/ \
  --set replicaCount=3 \
  --set image.tag=v1.0.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.company.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set resources.requests.cpu=200m \
  --set resources.requests.memory=256Mi
```

### Enable Auto-scaling
```bash
helm install currency-converter helm/currency-converter/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=20 \
  --set autoscaling.targetCPUUtilizationPercentage=70
```

### Enable Redis for Caching
```bash
helm install currency-converter helm/currency-converter/ \
  --set redis.enabled=true \
  --set redis.host=my-redis-service \
  --set redis.port=6379
```

## Upgrading

```bash
helm upgrade currency-converter helm/currency-converter/ \
  --set image.tag=v1.1.0
```

## Uninstallation

```bash
helm uninstall currency-converter
```

## Testing the Deployment

After installation, test the service:

```bash
# Port forward to access the service
kubectl port-forward svc/currency-converter 8080:80

# Test health endpoint
curl http://localhost:8080/health

# Test currency conversion
curl "http://localhost:8080/convert?ccy_from=USD&ccy_to=GBP&quantity=1000"
```

## Monitoring

To enable Prometheus monitoring, set:
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

## Security

The chart includes security best practices:
- Non-root container execution
- Read-only root filesystem
- Dropped capabilities
- Security contexts
- Service accounts

## Troubleshooting

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/name=currency-converter
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=currency-converter
```

### Debug deployment
```bash
helm template currency-converter helm/currency-converter/ --debug
```