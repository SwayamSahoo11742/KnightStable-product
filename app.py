from flask import Flask, request, session
from flask_session import Session
from helpers import strip_eval, cap
from flask_socketio import SocketIO
from flask_ngrok import run_with_ngrok
from config import Config
import psycopg2
import os
db = "postgres://gosegepgoehqhg:e23cf1d5e2e573d889d6a1b1d6e8ff0faefdd30a3f90d048bbb7965934a44c2c@ec2-34-197-84-74.compute-1.amazonaws.com:5432/d6gt830qsdsj7a"
# App
app = Flask(__name__)
# App Config
app.config.from_object(Config)
Session(app)

DATABASE_URL = os.environ.get('DATABASE_URL')


# Adding custom functions
app.jinja_env.globals.update(strip_eval=strip_eval)
app.jinja_env.globals.update(cap=cap)

socketio = SocketIO(app)
# Blueprint imports
from users.routes import users
from user_profile.routes import profiling
from search.routes import searches
from main.routes import main
from game.routes import chess

# Registering blueprints

app.register_blueprint(users)
app.register_blueprint(profiling)
app.register_blueprint(searches)
app.register_blueprint(main)
app.register_blueprint(chess)



# Connecting to database

# Running

if __name__ == "__main__":
    socketio.run(app)
