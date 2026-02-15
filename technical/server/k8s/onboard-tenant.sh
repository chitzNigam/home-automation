#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <tenant_username> <tenant_password> [namespace]"
  exit 1
fi

TENANT_USER="$1"
TENANT_PASS="$2"
NAMESPACE="${3:-home-automation}"
BROKER_SECRET="mosquitto-passwords"
BROKER_STS="mosquitto"

if [[ "$TENANT_USER" == "api" ]]; then
  echo "Refusing to modify reserved user 'api'."
  exit 1
fi

BROKER_POD="$(kubectl get pods -n "$NAMESPACE" -l app=mosquitto -o jsonpath='{.items[0].metadata.name}')"
if [[ -z "$BROKER_POD" ]]; then
  echo "No mosquitto pod found in namespace '$NAMESPACE'."
  exit 1
fi

HASHED_LINE="$(
  kubectl exec -n "$NAMESPACE" "$BROKER_POD" -- sh -lc \
    "mosquitto_passwd -b -c /tmp/passwd '$TENANT_USER' '$TENANT_PASS' >/dev/null && cat /tmp/passwd && rm -f /tmp/passwd"
)"

CURRENT_FILE="$(mktemp)"
UPDATED_FILE="$(mktemp)"
trap 'rm -f "$CURRENT_FILE" "$UPDATED_FILE"' EXIT

if kubectl get secret "$BROKER_SECRET" -n "$NAMESPACE" >/dev/null 2>&1; then
  kubectl get secret "$BROKER_SECRET" -n "$NAMESPACE" -o jsonpath='{.data.passwd}' | base64 -d > "$CURRENT_FILE"
else
  : > "$CURRENT_FILE"
fi

if grep -q "^${TENANT_USER}:" "$CURRENT_FILE"; then
  awk -v u="$TENANT_USER" -v line="$HASHED_LINE" -F: 'BEGIN{OFS=":"} $1==u {$0=line} {print}' "$CURRENT_FILE" > "$UPDATED_FILE"
else
  cat "$CURRENT_FILE" > "$UPDATED_FILE"
  if [[ -s "$UPDATED_FILE" ]]; then
    printf '\n' >> "$UPDATED_FILE"
  fi
  printf '%s\n' "$HASHED_LINE" >> "$UPDATED_FILE"
fi

kubectl create secret generic "$BROKER_SECRET" -n "$NAMESPACE" \
  --from-file=passwd="$UPDATED_FILE" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart statefulset/"$BROKER_STS" -n "$NAMESPACE"
kubectl rollout status statefulset/"$BROKER_STS" -n "$NAMESPACE" --timeout=300s

echo "Tenant '$TENANT_USER' is now in secret '$BROKER_SECRET' and mosquitto was restarted."
