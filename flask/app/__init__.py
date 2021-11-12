from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
print("__init__py started")
from app import views