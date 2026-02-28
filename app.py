import os
from flask import Flask
from flask_cors import CORS
import datetime
from db import db, client

app = Flask(__name__)
CORS(app)



from api.project_routes import project_bp
app.register_blueprint(project_bp)

if __name__ == "__main__":
    app.run(debug=True)
