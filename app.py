
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

from airportsearch import get_airport
from pricesearch import get_price
import re

