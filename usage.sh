#!/bin/sh

# Generate random username: bobXXXXX
USERNAME="bob$(shuf -i 10000-99999 -n 1)"
echo "Using username: $USERNAME"

# Register using auth service
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "splinter"}' || true

# Login using auth service
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "'$USERNAME'", "password": "splinter"}')

# Extract token and user_id
TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"access_token"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
USER_ID=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"user_id"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
echo "Token: $TOKEN"
echo "User ID: $USER_ID"

# Create a project
curl -X POST http://localhost:5000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"slug": "my-project", "name": "My Project", "description": "A sample project"}'

echo "---"

# Get all projects for a user
curl http://localhost:5000/projects -H "Authorization: Bearer $TOKEN"

echo "---"

# Get project details
curl http://localhost:5000/projects/my-project -H "Authorization: Bearer $TOKEN"

echo "---"

# Join a project
curl -X POST http://localhost:5000/projects/my-project/join -H "Authorization: Bearer $TOKEN"
