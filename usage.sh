#!/bin/sh
set -eu

PROJECT_URL="${PROJECT_URL:-http://localhost:5000}"
TOKEN="token-alice$(shuf -i 10000-99999 -n 1)"
TOKEN2="token-bob$(shuf -i 10000-99999 -n 1)"

echo "Using token: $TOKEN"
echo "Using token2: $TOKEN2"

SLUG="project-slug-$(shuf -i 10000-99999 -n 1)"
echo "Using slug: $SLUG"

echo "CREATING A NEW PROJECT"
curl -sS -X POST "$PROJECT_URL/projects" \
  -w "HTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"slug": "'$SLUG'", "name": "My Project", "description": "A sample project"}'
echo

echo "CREATING A NEW PROJECT (again)"
curl -sS -X POST "$PROJECT_URL/projects" \
  -w "HTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"slug": "'$SLUG'-2", "name": "My Project", "description": "A sample project"}'
echo

echo "CREATING A NEW PROJECT (WITH INVALID TOKEN, SHOULD FAIL)"
curl -sS -X POST "$PROJECT_URL/projects" \
  -w "HTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer not-a-real-token" \
  -d '{"slug": "'$SLUG'-3", "name": "My Project", "description": "A sample project"}'
echo

echo "GETTING ALL PROJECTS FOR USER"
curl -sS "$PROJECT_URL/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "GETTING ALL PROJECTS FOR USER (WITH INVALID TOKEN, SHOULD FAIL)"
curl -sS "$PROJECT_URL/projects" \
  -H "Authorization: Bearer not-a-real-token" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "GETTING PROJECT DETAILS FOR JUST-CREATED PROJECT"
curl -sS "$PROJECT_URL/projects/$SLUG" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "JOINING A PROJECT WE ARE ALREADY IN - THIS SHOULD RETURN ERROR"
curl -sS -X POST "$PROJECT_URL/projects/$SLUG/join" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "JOINING PROJECT AS SECOND USER"
curl -sS -X POST "$PROJECT_URL/projects/$SLUG/join" \
  -H "Authorization: Bearer $TOKEN2" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "LEAVING PROJECT AS SECOND USER"
curl -sS -X POST "$PROJECT_URL/projects/$SLUG/leave" \
  -H "Authorization: Bearer $TOKEN2" \
  -w "HTTP_STATUS:%{http_code}\n"
echo

echo "LEAVING PROJECT AS LAST USER - THIS SHOULD RETURN ERROR"
curl -sS -X POST "$PROJECT_URL/projects/$SLUG/leave" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP_STATUS:%{http_code}\n"
echo