# cloud-native project management service!!!!

## For Consumers

This service exposes REST API endpoints for project management.

**Note:** The API base URL is currently a placeholder. The actual URL will be provided after deployment (e.g., to Heroku or another cloud provider).

Replace `https://project-management.com` with the real URL once available. We suggest storing this in an environment variable so it can be easily swapped out.

### Endpoints

- **Create a project**
	- POST `/projects`
	- JSON body: `{ "slug": "unique-slug", "name": "Project Name", "description": "Optional description" }`
	- Example:
		```sh
		curl -X POST https://project-management.com/projects \
			-H "Content-Type: application/json" \
			-d '{"slug": "my-project", "name": "My Project", "description": "A sample project"}'
		```

- **Get all projects for a user**
	- GET `/projects`
	- Example:
		```sh
		curl https://project-management.com/projects
		```

- **Get project details**
	- GET `/projects/<slug>`
	- Example:
		```sh
		curl https://project-management.com/projects/my-project
		```

- **Join a project**
	- POST `/projects/<slug>/join`
	- Example:
		```sh
		curl -X POST https://project-management.com/projects/my-project/join
		```


## For Developers
### Getting started
Create a `.env` file. You can copy the `.env.example` file, 
```sh
cp .env.example .env
```

Setup your python virtual environment
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Source .env and go
```sh
source .env
flask run
```

### run_full_stack.sh
This script runs:
- a local mock of the UserAuth service
- our ProjectManagement service

### Usage.sh
This script will run through all the curl requests that our app can expect to make.
```sh
usage.sh
```