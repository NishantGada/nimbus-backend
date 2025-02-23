from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from notes import notes_bp
from users import users_bp
from tasks import tasks_bp
from noteCategories import noteCategories_bp
from links import links_bp
from linkCategories import link_categories_bp
from dbconfig import *

app = Flask(__name__)
CORS(app)
app.register_blueprint(notes_bp)
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(noteCategories_bp)
app.register_blueprint(links_bp)
app.register_blueprint(link_categories_bp)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask API"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)