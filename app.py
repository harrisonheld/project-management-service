import os
from flask import Flask
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from flask_cors import CORS
import datetime
from db import db, client
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

app.config['SWAGGER'] = {
    'title': 'Project Management API',
    'uiversion': 3,
}

swagger = Swagger(app, template={
    'swagger': '2.0',
    'info': {
        'title': 'Project Management API',
        'version': '1.0'
    },
    'securityDefinitions': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter: Bearer <your_token>'
        }
    }
})

from api.project_routes import project_bp
app.register_blueprint(project_bp)

@app.route('/')
def health_check():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    print(port)
    app.run(debug=True, port=port)
