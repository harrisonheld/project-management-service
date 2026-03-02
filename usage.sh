#!/bin/sh


# Load service URLs from environment or use defaults
AUTH_URL="${USERAUTH_SERVICE_URL:-http://localhost:5001/auth}"
HARDWARE_URL="${HARDWARE_SERVICE_URL:-http://localhost:5002/hardware}"
# this one is us :D we dont need to store it in the env lol
PROJECT_URL="http://localhost:5000"

# Generate random username: bobXXXXX
USERNAME="bob$(shuf -i 10000-99999 -n 1)"
echo "Using username: $USERNAME"



# Register using auth service
echo "REGISTERING NEW USER"
curl -X POST "$AUTH_URL/register" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "splinter"}' || true
echo "\n"

echo "REGISTERING ANOTHER USER WITH SAME USERNAME"
curl -X POST "$AUTH_URL/register" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "splinter"}' || true
echo "\n"

# Login using auth service
echo "LOGGING IN WITH NONEXISTANT USERNAME"
curl -s -X POST "$AUTH_URL/login" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"username": "doesnotexist", "password": "splinter"}'
echo "\n"

echo "LOGGING IN WITH WRONG PASSWORD"
curl -s -X POST "$AUTH_URL/login" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "wrongpassword"}'
echo "\n"

echo "LOGGING IN WITH NEW USER"
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/login" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "splinter"}')
echo "$LOGIN_RESPONSE"

# Extract token and user_id
TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"access_token"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
USER_ID=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"user_id"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
echo "Token: $TOKEN"
echo "User ID: $USER_ID"
echo "\n"



# Validate good token using auth service
echo "VALIDATING RETURNED TOKEN"
curl -X POST "$AUTH_URL/validate" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"access_token": "'$TOKEN'"}'
echo "\n"



# Validate a bad token using auth service
echo "VALIDATING A BAD TOKEN"
curl -X POST "$AUTH_URL/validate" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"access_token": "randomfaketoken"}'
echo "\n"


SLUG="project-slug-$(shuf -i 10000-99999 -n 1)"
echo "Using slug: $SLUG"



# Create a project
echo "CREATING A NEW PROJECT"
curl -X POST "$PROJECT_URL/projects" \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"slug": "'$SLUG'", "name": "My Project", "description": "A sample project"}'
echo "\n"



# Get all projects for a user
echo "GETTING ALL PROJECTS FOR USER"
curl "$PROJECT_URL/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_STATUS:%{http_code}\n"
echo "\n"



# Get project details
echo "GETTING PROJECT DETAILS FOR JUST-CREATED PROJECT"
curl "$PROJECT_URL/projects/$SLUG" \
  -H "Authorization: Bearer $TOKEN"  \
  -w "\nHTTP_STATUS:%{http_code}\n" 
echo "\n"



# Join a project
echo "JOINING A PROJECT WE ARE ALREADY IN"
curl -X POST "$PROJECT_URL/projects/$SLUG/join" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_STATUS:%{http_code}\n" 
echo "\n"