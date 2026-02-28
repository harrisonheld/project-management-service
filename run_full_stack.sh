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

# Start mock services in background
echo "Starting mock UserAuth service..."
(cd mocks && python mock_auth.py &)
MOCK_USERAUTH_PID=$!
sleep 2
echo "Starting mock HardwareManagement service..."
(cd mocks && python mock_hardware.py &)
MOCK_HARDWARE_PID=$!
sleep 2

# Kill mocks on exit (^C)
trap "kill $MOCK_USERAUTH_PID 2>/dev/null; kill $MOCK_HARDWARE_PID 2>/dev/null" EXIT

# Start main ProjectManagement Flask app (foreground)
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

# Wait for Flask to exit (trap will run after)
wait
