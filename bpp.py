
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import bcrypt
from datetime import timedelta

from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt


app = Flask(__name__)

app.config.from_pyfile('config.py')

mongo = PyMongo(app)
bus_id = 24  # Example bus_id
timings = list(mongo.db.bus_timing.find({"bus_id": bus_id}))
print(timings)