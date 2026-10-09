#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost"
echo "==> Starting Smoke Test on ${BASE_URL}..."

echo "[1/5] Checking Frontend / Nginx root..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/")
if [ "$CODE" -ne 200 ]; then
  echo "FAIL: GET / returned status $CODE"
  exit 1
fi
echo "OK (200)"

echo "[2/5] Checking Health Endpoint..."
HEALTH_BODY=$(curl -s "${BASE_URL}/api/health/")
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/health/")
if [ "$CODE" -ne 200 ]; then
  echo "FAIL: GET /api/health/ returned status $CODE"
  exit 1
fi
echo "OK: $HEALTH_BODY"

echo "[3/5] Checking unauthorized access to /api/tasks/..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/tasks/")
if [ "$CODE" -ne 401 ]; then
  echo "FAIL: Expected 401 Unauthorized, got $CODE"
  exit 1
fi
echo "OK (401)"

echo "[4/5] Checking Auth & Authenticated Request..."
TEST_USER="smoke_user_$(date +%s)"
TEST_PASS="SmokePass123!"

TOKEN=$(curl -s -X POST "${BASE_URL}/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${TEST_USER}\", \"password\": \"${TEST_PASS}\"}" | grep -o '"access":"[^"]*' | grep -o '[^"]*$') || true

if [ -z "$TOKEN" ]; then
  echo "INFO: User doesn't exist, creating test user via Docker..."
  docker compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='${TEST_USER}').exists() or User.objects.create_user('${TEST_USER}', 'smoke@test.com', '${TEST_PASS}')"

  TOKEN=$(curl -s -X POST "${BASE_URL}/api/token/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${TEST_USER}\", \"password\": \"${TEST_PASS}\"}" | grep -o '"access":"[^"]*' | grep -o '[^"]*$')
fi

CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/tasks/" -H "Authorization: Bearer ${TOKEN}")
if [ "$CODE" -ne 200 ]; then
  echo "FAIL: Authorized GET /api/tasks/ returned status $CODE"
  exit 1
fi
echo "OK (200 with JWT)"

echo "[5/5] Checking Swagger UI..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/docs/")
if [ "$CODE" -ne 200 ]; then
  echo "FAIL: GET /api/docs/ returned status $CODE"
  exit 1
fi
echo "OK (200)"

echo "==> ALL SMOKE TESTS PASSED SUCCESSFULLY! <=="