from flask import Flask, request, session
from flask_session import Session
from knightstable.helpers import strip_eval, cap
from flask_socketio import SocketIO
from flask_ngrok import run_with_ngrok
from knightstable.config import Config

# App
app = Flask(__name__)
# App Config
app.config.from_object(Config)
Session(app)


# Adding custom functions
app.jinja_env.globals.update(strip_eval=strip_eval)
app.jinja_env.globals.update(cap=cap)

socketio = SocketIO(app)
# Blueprint imports
from knightstable.users.routes import users
from knightstable.user_profile.routes import profiling
from knightstable.search.routes import searches
from knightstable.main.routes import main
from knightstable.game.routes import chess

# Registering blueprints

app.register_blueprint(users)
app.register_blueprint(profiling)
app.register_blueprint(searches)
app.register_blueprint(main)
app.register_blueprint(chess)


run_with_ngrok(app)

# Connecting to database
db = "C:/Users/Dodo/Desktop/Projects/games.db"

# Running

if __name__ == "__main__":
    socketio.run(app)
