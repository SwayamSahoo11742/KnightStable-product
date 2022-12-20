import random
import json
import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, current_app
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import strip_eval, cap, attempt
from flask_socketio import SocketIO, send
from flask_ngrok import run_with_ngrok

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "a7sak1yucEopmwbXLVZzPPuCMJ3RteFS"
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Adding custom functions
app.jinja_env.globals.update(strip_eval=strip_eval)
app.jinja_env.globals.update(cap=cap)

run_with_ngrok(app)

# Connecting to database
db = "C:/Users/Dodo/Desktop/Projects/games.db"
# -------------------------------------SOCKETIO-----------------------------------------------------------------#
socketio = SocketIO(app)

# When connected to /play
@socketio.on("connect", namespace="/play")
def connect(data):
    # Send back current game info
    data = session["curr_game"]
    data["selfname"] = session["username"]
    send(data, namespace="/play")


# When a move is made
@socketio.on("moved", namespace="/play")
def message(data):
    # Send the moved event back
    socketio.emit("moved", data, namespace="/play", broadcast=True)


# When game is over
@socketio.on("gameOver", namespace="/play")
def game_over(gameinfo):
    # If winner is black
    if gameinfo["winner"] == "black":
        # Set loser to white
        loser = gameinfo["data"]["white"]
        # Declare the rating modifiers
        winner_mod = gameinfo["black"]
        loser_mod = gameinfo["white"]
        # Winner is winner
        winner = gameinfo["data"][gameinfo["winner"]]
    # If draw or aborted
    elif gameinfo["winner"] == "none":
        # This section doesnt make sense, but for efficiency of code, 
        # the loser and loser_mod is to white
        # and winner and winner_mod is to black 
        # (To make clear, the status (winner/loser) do not have anything to do with the color in this case)
        loser = gameinfo["data"]["white"]
        loser_mod = gameinfo["white"]
        winner = gameinfo["data"]["black"]
        winner_mod = gameinfo["black"]
    # If white winner
    else:
        # Loser is black
        loser = gameinfo["data"]["black"]
        # Declaring modifiers
        winner_mod = gameinfo["white"]
        loser_mod = gameinfo["black"]
        # Winner is winner
        winner = gameinfo["data"][gameinfo["winner"]]
    # Connect to db
    game = sqlite3.connect(db)
    cursor = game.cursor()
    # Setting game status to end and pgn to appropriate pgn
    cursor.execute(
        "UPDATE ksgame SET status = 'ended', pgn = ? WHERE game_id = ?",
        (gameinfo["pgn"], gameinfo["data"]["game_id"]),
    )
    # Setting winner's rating
    winner_rating = cursor.execute(
        "SELECT rating FROM users WHERE username = ?", (winner,)
    ).fetchone()[0]
    print(winner_rating)
    cursor.execute(
        "UPDATE users SET rating = ? WHERE username = ?",
        (winner_rating + winner_mod, winner),
    )
    # Setting loser's rating
    loser_rating = cursor.execute(
        "SELECT rating FROM users WHERE username = ?", (loser,)
    ).fetchone()[0]
    cursor.execute(
        "UPDATE users SET rating = ? WHERE username = ?",
        (loser_rating + loser_mod, loser),
    )
    # Commiting
    game.commit()
    # Sending back the winner and rating modifiers to display on player's screen
    socketio.emit(
        "gameOver",
        {"winner": winner, "winner_mod": winner_mod, "loser_mod": loser_mod},
        namespace="/play",
        broadcast=True,
    )


# -------------------------------------FLASK ROUTES--------------------------------------------------------------#
# Register Page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # returninf template
        return render_template("register.html", logged=attempt(session, "logged"))
    else:
        # Connecting to db
        users = sqlite3.connect(db)
        cursor = users.cursor()

        # Getting user's input
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        # Setting up and executing query for username search
        query = "SELECT COUNT(username) FROM users WHERE username = ?"
        db_users = cursor.execute(query, (username,))
        db_users = db_users.fetchone()[0]

        # Checking for invalid usernames or emails or passwords
        if len(username) < 4:
            flash("Invalid username (Too short)", "error")
            return redirect("/register")

        if len(password) < 6:
            flash("Invalid password (Too short)", "error")
            return redirect("/register")

        if not request.form.get("email"):
            flash("No email provided", "error")
            return redirect("/register")
        # Looking to see if same username in db
        if db_users != 0:
            flash("Username Taken", "error")
            return redirect("/register")

        # Looking to see if same email
        query = "SELECT COUNT(email) FROM users WHERE email = ?"
        db_emails = cursor.execute(query, (email,))
        db_emails = db_emails.fetchone()[0]
        if db_emails != 0:
            flash("Email already registered", "error")
            return redirect("/register")

        # Checking if password confirmation was succesful
        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect("/register")

        # Generating passwrod hash
        hash = generate_password_hash(password)

        # Setting up and executing query
        query = "INSERT INTO users (username, email, hash) VALUES (?,?,?)"
        data_tuple = (username, email, hash)
        cursor.execute(query, data_tuple)

        # Commiting and closing
        users.commit()
        users.close()
        session["logged"] = True
        flash("Successfully registered")
        return redirect("/")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", logged=attempt(session, "logged"))
    else:
        users = sqlite3.connect(db)
        users.row_factory = sqlite3.Row
        cursor = users.cursor()

        # Checking for valid username
        if not request.form.get("username"):
            flash("Username was not provided")
            return redirect("/login")

        # Checking for valid password
        if not request.form.get("password"):
            flash("Password was not provided")
            return redirect("/login")
        # Checking for matching username and pass
        user_rows = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()
        if len(user_rows) != 1 or not check_password_hash(
            user_rows[0]["hash"], request.form.get("password")
        ):
            flash("Password and Username did not match", "error")
            return redirect("/login")

        # Setting user id and logged status to true
        session["user_id"] = user_rows[0]["id"]
        session["username"] = user_rows[0]["username"]
        session["logged"] = True
        flash("Logged in Successfully")
        return redirect("/")


# Logout page


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logout.html", logged=attempt(session, "logged"))
    else:
        # Logging user out
        session["logged"] == False
        # Clearing login session
        session.clear()
        return redirect("/")


# Home page


@app.route("/")
def home():

    return render_template("index.html", logged=attempt(session, "logged"))


# Search Page
@app.route("/search", methods=["POST", "GET"])
def search():
    # If get render template
    if request.method == "GET":

        return render_template("search.html", logged=attempt(session, "logged"))
    else:
        # Connecting to server
        games = sqlite3.connect(db)
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
            data_tuple = (
                "%" + black_user + "%",
                "%" + white_user + "%",
                "%" + moves + "%",
                "%" + opening + "%",
                max_rating,
                min_rating,
                result,
            )

            valid_games = cursor.execute(query, data_tuple)

            # Making a list of dictionaries with the game data
            result = [dict(row) for row in valid_games]

            cursor.close()
            return render_template(
                "search.html", games=result, logged=attempt(session, "logged")
            )
        else:
            # Defining Query
            query = "SELECT * FROM games WHERE black LIKE ? AND white LIKE ? AND moves LIKE ? AND opening LIKE ? AND white_elo <= ? AND white_elo >= ? LIMIT(50)"

            # Creating a tuple for the values that will go into the query
            data_tuple = (
                "%" + black_user + "%",
                "%" + white_user + "%",
                "%" + moves + "%",
                "%" + opening + "%",
                max_rating,
                min_rating,
            )

            valid_games = cursor.execute(query, data_tuple)

            # Making a list of dictionaries with the game data
            results = [dict(row) for row in valid_games]

            cursor.close()
            return render_template(
                "search.html",
                logged=attempt(session, "logged"),
                games=results,
                black_user=black_user,
                white_user=white_user,
                result=result,
                max_rating=max_rating,
                min_rating=min_rating,
                moves=moves,
                opening=opening,
            )


# Opening search
@app.route("/openings", methods=["GET", "POST"])
def openings():
    # Checking if request is GET
    if request.method == "GET":
        # Render template
        return render_template("openings.html", logged=attempt(session, "logged"))
    else:
        # Connect to db
        games = sqlite3.connect(db)

        # Enabling Row Factory
        games.row_factory = sqlite3.Row

        # Creating cursor object
        cursor = games.cursor()

        # Getting selected color , opening and moves (PGN format) values
        color = request.form.get("color")
        name = request.form.get("opening")
        moves = request.form.get("moves")

        # checking if If Color is not "Any" ( This needs to be checked because db does not have a value "Any" for color)
        if color != "Any":
            # Create a query with color as a value in data tuple
            query = "SELECT * FROM opening WHERE color LIKE ? AND name LIKE ? AND moves LIKE ?"
            data_tuple = (color, "%" + name + "%", "%" + moves + "%")
        else:
            # Creating a query with color not as it's value in the data tuple
            query = "SELECT * FROM opening WHERE name LIKE ? AND moves LIKE ?"
            data_tuple = ("%" + name + "%", "%" + moves + "%")

        # Getting openings that match query
        openings = cursor.execute(query, data_tuple)
        # Turning into a dict object
        openings = [dict(row) for row in openings]
        # Closing cursor object
        cursor.close()

        # Returning template
        return render_template(
            "openings.html",
            logged=attempt(session, "logged"),
            openings=openings,
            color=color.capitalize(),
            moves=moves,
            name=name.capitalize(),
        )


# Reccomended Page
@app.route("/recommended")
def recommended():
    # This is a static template, therefore only returning template
    return render_template("recommended.html", logged=attempt(session, "logged"))


# Page where the game playing will be commenced
# Dynamic to support different rooms
@app.route("/play/<id>")
def game(id):
    # Seems empty, because matchmaking and settings handling is done at "/play", where they select the settinsg they want and matchmade there as well
    # Rendering template
    return render_template("game.html", logged=attempt(session, "logged"))


# Page where the settings and matchmaking is handled
@app.route("/play", methods=["POST", "GET"])
def play():
    # If GET request, render template
    if request.method == "GET":
        return render_template("play.html", logged=attempt(session, "logged"))
    # If POST
    else:
        # Get specified customizations
        time = request.form.get("time")
        rated = request.form.get("rated")
        # Connect to db
        games = sqlite3.connect(db)
        # Enable row factory
        games.row_factory = sqlite3.Row
        # Create a cursor object
        cursor = games.cursor()
        # Getting the rating of the player
        rating = cursor.execute(
            "SELECT rating FROM users WHERE id = ?", (session["user_id"],)
        )
        rating = [dict(row) for row in rating][0]["rating"]
        # Retrieving all the games that match user's specifications and are searching
        pending_games = cursor.execute(
            "SELECT game_id FROM ksgame WHERE status = 'searching' AND time = ? AND rated = ? AND white != ? LIMIT 1",
            (time, rated, session["user_id"]),
        )
        # Turning into a dict object
        pending_games = [dict(row) for row in pending_games]

        # If pending games available
        if len(pending_games) >= 1:
            # Add user to as black and set staus to ongoing
            cursor.execute(
                "UPDATE ksgame SET black = ?, status = 'ongoing', black_rating = ? WHERE game_id = ?",
                (session["user_id"], rating, pending_games[0]["game_id"]),
            )
            # Commit
            games.commit()
            # Getting current game info
            curr_game = cursor.execute(
                "SELECT * FROM ksgame WHERE game_id = ?", (pending_games[0]["game_id"],)
            )
            curr_game = [dict(row) for row in curr_game][0]
            # Turning player id's to username
            blackuser = cursor.execute(
                "SELECT username FROM users WHERE id = ?", (curr_game["black"],)
            )
            blackuser = [dict(row) for row in blackuser][0]["username"]
            whiteuser = cursor.execute(
                "SELECT username FROM users WHERE id = ?", (curr_game["white"],)
            )
            whiteuser = [dict(row) for row in whiteuser][0]["username"]
            # Updating curr_game with the correct names
            curr_game["black"] = blackuser
            curr_game["white"] = whiteuser

            # Saving to cookie session
            session["curr_game"] = curr_game
            # # Redirect to play/ {gameid of the game}
            return redirect("/play/" + str(pending_games[0]["game_id"]))
        # If no pending available
        else:
            # Adding user as white if no pending available, and adding the game params with it
            cursor.execute(
                "INSERT INTO ksgame (white, status, time, rated, white_rating) VALUES (?,?,?,?,?)",
                (session["user_id"], "searching", time, rated, rating),
            )
            # Adding the link to the db
            cursor.execute(
                "UPDATE ksgame SET site = ? WHERE game_id = ?",
                (
                    "http://127.0.0.1:5000/play/" + str(cursor.lastrowid),
                    cursor.lastrowid,
                ),
            )
            # Commiting changes
            games.commit()

            # Setting a boolean to keep track of black player's presence
            black_player = False

            # As long as black player is not here
            while not black_player:
                # Keep looking if any joined
                black = cursor.execute(
                    "SELECT black FROM ksgame WHERE game_id = ?", (cursor.lastrowid,)
                )
                # If a black player has joined
                black = [dict(row) for row in black]
                if black[0]["black"] != None:
                    # Set black_player boolean to true to stop the wait
                    black_player = True

            # Getting current game info
            curr_game = cursor.execute(
                "SELECT * FROM ksgame WHERE game_id = ?", (cursor.lastrowid,)
            )
            curr_game = [dict(row) for row in curr_game][0]
            # Turning player id's to username
            blackuser = cursor.execute(
                "SELECT username FROM users WHERE id = ?", (curr_game["black"],)
            )
            blackuser = [dict(row) for row in blackuser][0]["username"]
            whiteuser = cursor.execute(
                "SELECT username FROM users WHERE id = ?", (curr_game["white"],)
            )
            whiteuser = [dict(row) for row in whiteuser][0]["username"]
            # Updating curr_game with the correct names
            curr_game["black"] = blackuser
            curr_game["white"] = whiteuser

            # Saving to cookie session
            session["curr_game"] = curr_game
            # Redirecting to their game url
            return redirect("/play/" + str(cursor.lastrowid))


if __name__ == "__main__":
    socketio.run(app)
