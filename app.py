import os 
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import strip_eval, cap

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connecting to database

app.jinja_env.globals.update(strip_eval=strip_eval)
app.jinja_env.globals.update(cap=cap)

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Search Page
@app.route("/search", methods=["POST","GET"])
def search():
    # If get render template
    if request.method == "GET":

        return render_template("search.html")
    else:
        # Connecting to server
        games = sqlite3.connect("games.db")
        games.row_factory = sqlite3.Row
        cursor = games.cursor()

        # Getting user input
        black_user = request.form.get("black-username")
        white_user = request.form.get("white-username")
        moves = request.form.get("moves")
        opening = request.form.get("opening")
        min_rating = request.form.get("min-rating")
        max_rating = request.form.get("max-rating")
        result = request.form.get("result")

        # Checking for result values
        if result != "Any":
            # Defining Query
            query = "SELECT * FROM games WHERE black LIKE ? AND white LIKE ? AND moves LIKE ? AND opening LIKE ? AND white_elo <= ? AND white_elo >= ? AND result = ? LIMIT(50)"
            
            # Creating a tuple for the values that will go into the query
            data_tuple = ("%"+black_user+"%", "%"+white_user+"%", "%"+moves+"%", "%"+opening+"%", max_rating, min_rating, result)
            
            valid_games = cursor.execute(query, data_tuple)
            
            # Making a list of dictionaries with the game data
            result = [dict(row) for row in valid_games]
            
            cursor.close()
            return render_template("search.html", games=result)
        else:
            # Defining Query
            query = "SELECT * FROM games WHERE black LIKE ? AND white LIKE ? AND moves LIKE ? AND opening LIKE ? AND white_elo <= ? AND white_elo >= ? LIMIT(50)"
            
            # Creating a tuple for the values that will go into the query
            data_tuple = ("%"+black_user+"%", "%"+white_user+"%", "%"+moves+"%", "%"+opening+"%", max_rating, min_rating)
            
            valid_games = cursor.execute(query, data_tuple)
            
            # Making a list of dictionaries with the game data
            results = [dict(row) for row in valid_games]
            
            cursor.close()
            print(white_user)
            return render_template("search.html", games=results, black_user=black_user, white_user=white_user, result=result, max_rating=max_rating, min_rating=min_rating, moves=moves, opening=opening)


# Opening search
@app.route("/openings", methods=["GET", "POST"])
def openings():
    if request.method == "GET":
        return render_template("openings.html")
    else:
        games = sqlite3.connect("games.db")
        games.row_factory = sqlite3.Row
        cursor = games.cursor()

        color = request.form.get("color")
        if color != "Any":
            name = request.form.get("opening")
            moves = request.form.get("moves")
            print(color)
            query = "SELECT * FROM opening WHERE color LIKE ? AND name LIKE ? AND moves LIKE ?"
            data_tuple = (color, "%"+name+"%", "%"+moves+"%")
            buffer = cursor.execute(query,data_tuple)
            openings = [dict(row) for row in buffer]
            cursor.close()
            return render_template("openings.html", openings=openings, color=color.capitalize(), moves=moves, name=name.capitalize())
        else:
            name = request.form.get("opening")
            moves = request.form.get("moves")
            print(color)
            query = "SELECT * FROM opening WHERE name LIKE ? AND moves LIKE ?"
            data_tuple = ("%"+name+"%", "%"+moves+"%")
            buffer = cursor.execute(query,data_tuple)
            openings = [dict(row) for row in buffer]
            cursor.close()
            return render_template("openings.html", openings=openings, color=color.capitalize(), moves=moves, name=name.capitalize())


# Reccomended Page
@app.route("/recommended")
def recommended():
    return render_template("recommended.html")

