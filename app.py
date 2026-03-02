import os
from flask import Flask
from flask_cors import CORS
import datetime
from db import db, client
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)



from api.project_routes import project_bp
app.register_blueprint(project_bp)

@app.route('/')
def health_check():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(debug=True)
