#!/bin/sh
set -eu

FLASK_RUN_PORT="${FLASK_RUN_PORT:-5000}"
PROJECT_URL="${PROJECT_URL:-http://localhost:${FLASK_RUN_PORT}}"
TOKEN="token-alice$(shuf -i 10000-99999 -n 1)"
TOKEN2="token-bob$(shuf -i 10000-99999 -n 1)"
INVALID_TOKEN="not-a-real-token"

echo "Using token: $TOKEN"
echo "Using token2: $TOKEN2"

SLUG="project-slug-$(shuf -i 10000-99999 -n 1)"
echo "Using slug: $SLUG"

FAILURES=0
HTTP_STATUS=""
HTTP_BODY=""

request() {
  method="$1"
  url="$2"
  token="$3"
  data="${4-}"

  if [ -n "$data" ]; then
    response=$(curl -sS -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $token" \
      -d "$data" \
      -w "\n%{http_code}")
  else
    response=$(curl -sS -X "$method" "$url" \
      -H "Authorization: Bearer $token" \
      -w "\n%{http_code}")
  fi

  HTTP_STATUS=$(printf "%s" "$response" | tail -n 1)
  HTTP_BODY=$(printf "%s" "$response" | sed '$d')
}

assert_status() {
  expected="$1"
  label="$2"
  if [ "$HTTP_STATUS" = "$expected" ]; then
    echo "PASS: $label (status=$HTTP_STATUS)"
  else
    echo "FAIL: $label (expected $expected got $HTTP_STATUS)"
    echo "BODY: $HTTP_BODY"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "[1] Create project"
request "POST" "$PROJECT_URL/projects" "$TOKEN" '{"slug": "'$SLUG'", "name": "My Project", "description": "A sample project"}'
assert_status "201" "create project"

echo "[2] Create second project"
request "POST" "$PROJECT_URL/projects" "$TOKEN" '{"slug": "'$SLUG'-2", "name": "My Project", "description": "A sample project"}'
assert_status "201" "create second project"

echo "[3] Create project with invalid token"
request "POST" "$PROJECT_URL/projects" "$INVALID_TOKEN" '{"slug": "'$SLUG'-3", "name": "My Project", "description": "A sample project"}'
assert_status "401" "invalid token create rejected"

echo "[4] Get projects for valid user"
request "GET" "$PROJECT_URL/projects" "$TOKEN"
assert_status "200" "get projects"

echo "[5] Get projects with invalid token"
request "GET" "$PROJECT_URL/projects" "$INVALID_TOKEN"
assert_status "401" "invalid token list rejected"

echo "[6] Get project details"
request "GET" "$PROJECT_URL/projects/$SLUG" "$TOKEN"
assert_status "200" "get project details"

echo "[7] Join as owner (already member)"
request "POST" "$PROJECT_URL/projects/$SLUG/join" "$TOKEN"
assert_status "400" "join already-member rejected"

echo "[8] Join as second user"
request "POST" "$PROJECT_URL/projects/$SLUG/join" "$TOKEN2"
assert_status "200" "join second user"

echo "[9] Membership check for owner"
request "GET" "$PROJECT_URL/projects/$SLUG/membership" "$TOKEN"
assert_status "200" "membership owner"

echo "[10] Leave as second user"
request "POST" "$PROJECT_URL/projects/$SLUG/leave" "$TOKEN2"
assert_status "200" "leave second user"

echo "[11] Leave as last user"
request "POST" "$PROJECT_URL/projects/$SLUG/leave" "$TOKEN"
assert_status "400" "last-user leave rejected"

if [ "$FAILURES" -gt 0 ]; then
  echo ""
  echo "smoke_http.sh FAILED ($FAILURES failing checks)"
  exit 1
fi

echo ""
echo "smoke_http.sh PASSED"