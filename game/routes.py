from flask import Blueprint
from flask import redirect, render_template, request, session,flash
from flask_socketio import send, join_room
import psycopg2
from psycopg2.extras import RealDictCursor
from app import db
import time
chess = Blueprint("chess", __name__)
from app import socketio

# -------------------------------------SOCKETIO-----------------------------------------------------------------#

# When aborted
@socketio.on("abort", namespace="/play")
def abort():
    socketio.emit("abort", namespace="/play", to=session["curr_game"]["game_id"])


# When a player has resigned
@socketio.on("resign", namespace="/play")
def resign():
    # Send back resign event
    socketio.emit("resign", namespace="/play", to=session["curr_game"]["game_id"])


# When connected to /play
@socketio.on("connect", namespace="/play")
def connect(data):
    # Send back current game info
    data = session["curr_game"]
    data["selfname"] = session["username"]
    room = session["curr_game"]["game_id"]
    data.pop('datetime')
    join_room(room)
    send(data, namespace="/play")


# When a move is made
@socketio.on("moved", namespace="/play")
def message(data):
    # Send the moved event back
    socketio.emit(
        "moved",
        data,
        namespace="/play",
        broadcast=True,
        to=session["curr_game"]["game_id"],
    )


# When game is over
@socketio.on("gameOver", namespace="/play")
def game_over(gameinfo):
    # Connect to db

    game = psycopg2.connect(db)
    cursor = game.cursor()

    # If aborted
    if gameinfo["winner"] == "abort":
        # Delete game from db
        cursor.execute(
            "DELETE FROM ksgame WHERE game_id = %s", (gameinfo["data"]["game_id"],)
        )
        # leave
        return

    # If winner is black
    if gameinfo["winner"] == "black":
        # Set loser to white
        loser = gameinfo["data"]["white"]
        # Declare the rating modifiers
        winner_mod = gameinfo["black"]
        loser_mod = gameinfo["white"]
        # Winner is winner
        winner = gameinfo["data"][gameinfo["winner"]]
        result = "0-1"
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
        result = "1-1"
    # If white winner
    else:
        # Loser is black
        loser = gameinfo["data"]["black"]
        # Declaring modifiers
        winner_mod = gameinfo["white"]
        loser_mod = gameinfo["black"]
        # Winner is winner
        winner = gameinfo["data"][gameinfo["winner"]]
        result = "1-0"
    # Setting game status to end and pgn to appropriate pgn
    cursor.execute(
        "UPDATE ksgame SET status = 'ended', pgn = %s, result = %s WHERE game_id = %s",
        (gameinfo["pgn"], result, gameinfo["data"]["game_id"]),
    )
    # Setting winner's rating
    cursor.execute(
        "SELECT rating FROM users WHERE username = %s", (winner,)
    )
    winner_rating = cursor.fetchone()[0]
    cursor.execute(
        "UPDATE users SET rating = %s WHERE username = %s",
        (winner_rating + winner_mod, winner),
    )
    # Setting loser's rating
    cursor.execute(
        "SELECT rating FROM users WHERE username = %s", (loser,)
    )
    loser_rating = cursor.fetchone()[0]

    # if loser's rating is below 100 (min)
    if loser_rating - loser_mod < 100:
        # set it to 100
        cursor.execute("UPDATE users SET rating = %s WHERE username = %s", (100, loser)),
    # else
    else:
        # Deduct as normal
        cursor.execute(
            "UPDATE users SET rating = %s WHERE username = %s",
            (loser_rating - loser_mod, loser),
        )
    # Commiting
    game.commit()
    # Sending back the winner and rating modifiers to display on player's screen
    socketio.emit(
        "gameOver",
        {"winner": winner, "winner_mod": winner_mod, "loser_mod": loser_mod},
        namespace="/play",
        to=session["curr_game"]["game_id"],
        broadcast=True,
    )


# ------------------------------------------------------------ROUTES_--------------------------------------------------
# Page where the game playing will be commenced
# Dynamic to support different rooms
@chess.route("/play/<id>")
def game(id):
    # Seems empty, because matchmaking and settings handling is done at "/play", where they select the settinsg they want and matchmade there as well
    # Connect to db
    if "logged" not in session:
        flash("You should login")
        return redirect("/")
    users = psycopg2.connect(db)
    cursor = users.cursor()
    # Getting pfps
    cursor.execute(
            "SELECT pfp FROM users WHERE username = %s", (session["curr_game"]["white"],)
        )
    white_pfp = "/static/img/pfp/" + cursor.fetchone()[0]

    cursor.execute(
            "SELECT pfp FROM users WHERE username = %s", (session["curr_game"]["white"],)
        )
    black_pfp = "/static/img/pfp/" + cursor.fetchone()[0]
    # Rendering template
    return render_template(
        "game.html",
        white_pfp=white_pfp,
        black_pfp=black_pfp,
    )


# Page where the settings and matchmaking is handled
@chess.route("/play", methods=["POST", "GET"])
def play():
    # If GET request, render template
    if request.method == "GET":
        if "logged" not in session:
            flash("You should login")
            return redirect("/")
        return render_template("play.html")
    # If POST
    else:
        if "logged" not in session:
            flash("You should login")
            return redirect("/")
        # Get specified customizations
        time_control = request.form.get("time")
        rated = request.form.get("rated")
        # Connect to db
        games = psycopg2.connect(db, cursor_factory=RealDictCursor)
        # Create a cursor object
        cursor = games.cursor()
        # Getting the rating of the player
        cursor.execute(
            "SELECT rating FROM users WHERE id = %s", (session["user_id"],)
        )
        rating = cursor.fetchall()
        rating = [dict(row) for row in rating][0]["rating"]
        # Retrieving all the games that match user's specifications and are searching
        cursor.execute(
            "SELECT game_id FROM ksgame WHERE status = 'searching' AND time = %s AND rated = %s AND white != %s LIMIT 1",
            (time_control, rated, session["username"]),
        )
        pending_games = cursor.fetchall()
        # Turning into a dict object
        pending_games = [dict(row) for row in pending_games]

        # If pending games available
        if len(pending_games) >= 1:
            # Add user to as black and set staus to ongoing
            cursor.execute(
                "UPDATE ksgame SET black = %s, status = 'ongoing', black_rating = %s WHERE game_id = %s",
                (session["username"], rating, pending_games[0]["game_id"]),
            )
            # Commit
            games.commit()
            # Getting current game info
            cursor.execute(
                "SELECT * FROM ksgame WHERE game_id = %s", (pending_games[0]["game_id"],)
            )
            curr_game = cursor.fetchall()
            curr_game = [dict(row) for row in curr_game][0]

            # Saving to cookie session
            session["curr_game"] = curr_game
            # # Redirect to play/ {gameid of the game}
            return redirect("/play/" + str(pending_games[0]["game_id"]))
        # If no pending available
        else:
            # Adding user as white if no pending available, and adding the game params with it
            cursor.execute(
                "INSERT INTO ksgame (white, status, time, rated, white_rating) VALUES (%s,%s,%s,%s,%s) RETURNING game_id",
                (session["username"], "searching", time_control, rated, rating),
            )
            lastrowid = cursor.fetchone()["game_id"]
            # Adding the link to the db
            cursor.execute(
                "UPDATE ksgame SET site = %s WHERE game_id = %s",
                (
                    "http://127.0.0.1:5000/play/" + str(lastrowid),
                    lastrowid,
                ),
            )
            # Commiting changes
            games.commit()

            # Setting a boolean to keep track of black player's presence
            black_player = False

            # As long as black player is not here
            while not black_player:
                time.sleep()
                # Keep looking if any joined
                cursor.execute(
                    "SELECT black FROM ksgame WHERE game_id = %s", (lastrowid,)
                )
                # If a black player has joined
                black = cursor.fetchall()
                black = [dict(row) for row in black]
                if black[0]["black"] != None:
                    # Set black_player boolean to true to stop the wait
                    black_player = True

            # Getting current game info
            cursor.execute(
                "SELECT * FROM ksgame WHERE game_id = %s", (lastrowid,)
            )
            curr_game = cursor.fetchall()
            curr_game = [dict(row) for row in curr_game][0]

            # Saving to cookie session
            session["curr_game"] = curr_game
            # Redirecting to their game url

            return redirect("/play/" + str(lastrowid))
