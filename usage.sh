#!/bin/sh

# Create a project
curl -X POST http://localhost:5000/projects \
  -H "Content-Type: application/json" \
  -d '{"slug": "my-project", "name": "My Project", "description": "A sample project"}'

echo "---"

# Get all projects for a user
curl http://localhost:5000/projects

echo "---"

# Get project details
curl http://localhost:5000/projects/my-project

echo "---"

# Join a project
curl -X POST http://localhost:5000/projects/my-project/join
