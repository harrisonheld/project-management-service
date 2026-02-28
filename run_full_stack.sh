#!/bin/bash
# Run the full ProjectManagement + mock UserAuth stack

set -e

# Source environment variables
if [ -f .env ]; then
    source .env
else
    echo ".env file not found. Please create it from .env.example."
    exit 1
fi

# Activate Python virtual environment
if [ -d venv ]; then
    source venv/bin/activate
else
    echo "Python venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Start mock UserAuth service in background
if [ -d mock_auth ]; then
    echo "Starting mock UserAuth service..."
    (cd mock_auth && source ../venv/bin/activate && python mock_auth.py &)
    MOCK_PID=$!
    sleep 2
else
    echo "mock_auth directory not found."
    exit 1
fi

# Ensure the mock service is killed on exit (Ctrl+C or error)
trap "kill $MOCK_PID 2>/dev/null" EXIT

# Start main ProjectManagement Flask app (foreground)
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

# Wait for Flask to exit (trap will run after)
wait
