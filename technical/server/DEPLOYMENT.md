# Home Automation Server Deployment (Kubernetes)

This document captures the end-to-end deployment flow for the server stack on Kubernetes, including API image loading for `kind`, secret creation from `.env`, verification, and common recovery steps.

## 1) Prerequisites

- Kubernetes context points to your cluster (example: `kind-home-automation`)
- `kubectl`, `docker`, and `kind` are installed
- Run commands from repo root:
  - `/home/chitz/proj/home-automation`

Quick checks:

```bash
kubectl config current-context
kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.containerRuntimeVersion}{"\n"}'
```

Expected runtime for this guide: `containerd://...` on `kind`.

## 2) Load Environment Variables

Always source secrets/config values from `technical/server/.env`.

```bash
set -a
source technical/server/.env
set +a
```

## 3) Namespace

```bash
NS=home-automation
kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create ns "$NS"
```

If your context already defaults to this namespace, you can skip `-n` flags in later commands.

## 4) Create ConfigMaps and Secrets (from `.env`)

### Postgres config + credentials

```bash
kubectl create configmap postgres-config \
  --from-literal=POSTGRES_DB="$POSTGRES_DB" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_USER="$POSTGRES_USER" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### API MQTT secret

`api.yaml` now pins `MQTT_USERNAME=api`, so this secret only needs `MQTT_PASSWORD`.

```bash
kubectl create secret generic api-secret \
  --from-literal=MQTT_PASSWORD="$MQTT_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Mosquitto certs + passwd file

```bash
kubectl create secret generic mosquitto-certs \
  --from-file=ca.crt=technical/server/mosquitto/certs/ca.crt \
  --from-file=server.crt=technical/server/mosquitto/certs/server.crt \
  --from-file=server.key=technical/server/mosquitto/certs/server.key \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic mosquitto-passwords \
  --from-file=passwd=technical/server/mosquitto/passwords/passwd \
  --dry-run=client -o yaml | kubectl apply -f -
```

## 5) Build and Load API Image to Kind

```bash
docker build -t esp-api:local technical/server/api
kind load docker-image esp-api:local --name home-automation
```

## 6) Apply Manifests

Apply dependencies first, then API.

```bash
kubectl apply -f technical/server/k8s/postgres.yaml
kubectl apply -f technical/server/k8s/redis.yaml
kubectl apply -f technical/server/k8s/mosquitto.yaml
kubectl apply -f technical/server/k8s/api.yaml
```

Wait for rollouts:

```bash
kubectl rollout status statefulset/postgres --timeout=300s
kubectl rollout status statefulset/redis --timeout=300s
kubectl rollout status statefulset/mosquitto --timeout=300s
kubectl rollout status deployment/api --timeout=300s
```

## 7) Verify Deployment Health

### Pod and service status

```bash
kubectl get pods -o wide
kubectl get svc
```

### API readiness

```bash
kubectl port-forward svc/api 5000:5000
```

In another shell:

```bash
curl -s http://127.0.0.1:5000/api/live
curl -s http://127.0.0.1:5000/api/ready
```

Expected readiness shape:

```json
{"checks":{"mqtt":true,"postgres":true,"redis":true},"status":"ready"}
```

### End-to-end state write test (Postgres + MQTT publish path)

```bash
curl -s -X POST http://127.0.0.1:5000/api/tenants/tenant1/devices/device1/state \
  -H 'Content-Type: application/json' \
  -d '{"state":"ON"}'
```

Look for:
- `stored` object returned
- `"mqtt_published": true`

## 8) Common Troubleshooting

### `ImagePullBackOff` for `esp-api:local`

Cause: image not loaded into kind nodes.

Fix:

```bash
docker build -t esp-api:local technical/server/api
kind load docker-image esp-api:local --name home-automation
kubectl rollout restart deployment/api
kubectl rollout status deployment/api --timeout=300s
```

### `CreateContainerConfigError` on API pod

Cause: missing Secret/ConfigMap.

Check:

```bash
kubectl describe pod -l app=api | sed -n '/Events/,$p'
```

### `mqtt:false` in `/api/ready`

Cause usually auth mismatch between:
- API secret (`api-secret` -> `MQTT_PASSWORD`)
- Broker password file (`mosquitto-passwords` secret, `api` user entry)

Broker logs:

```bash
kubectl logs statefulset/mosquitto --tail=200 | egrep -i 'not authorised|auth|tls|error'
```

If needed, update API secret from `.env`, then restart API:

```bash
set -a; source technical/server/.env; set +a
kubectl create secret generic api-secret \
  --from-literal=MQTT_PASSWORD="$MQTT_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/api
kubectl rollout status deployment/api --timeout=300s
```

## 9) Tenant Onboarding (No API Redeploy)

Use the helper script:

```bash
technical/server/k8s/onboard-tenant.sh <tenant_username> <tenant_password> [namespace]
```

Example:

```bash
technical/server/k8s/onboard-tenant.sh tenant3 'tenant3-password' home-automation
```

What it does:
- Reads current `mosquitto-passwords` secret
- Adds/updates one tenant credential line
- Applies updated secret
- Restarts only Mosquitto StatefulSet

API deployment does not need redeploy for new tenants.

## 10) API-Only Redeploy

```bash
set -a
source technical/server/.env
set +a

docker build -t esp-api:local technical/server/api
kind load docker-image esp-api:local --name home-automation

kubectl create secret generic api-secret \
  --from-literal=MQTT_PASSWORD="$MQTT_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f technical/server/k8s/api.yaml
kubectl rollout restart deployment/api
kubectl rollout status deployment/api --timeout=300s
```
