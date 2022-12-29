from flask import Blueprint
import sqlite3
from flask import redirect, render_template, request, session
from flask_socketio import send, join_room

db = "games.db"
chess = Blueprint("chess", __name__)
from .. import socketio

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
    game = sqlite3.connect(db)
    cursor = game.cursor()

    # If aborted
    if gameinfo["winner"] == "abort":
        # Delete game from db
        cursor.execute(
            "DELETE FROM ksgame WHERE game_id = ?", (gameinfo["data"]["game_id"],)
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
        "UPDATE ksgame SET status = 'ended', pgn = ?, result = ? WHERE game_id = ?",
        (gameinfo["pgn"], result, gameinfo["data"]["game_id"]),
    )
    # Setting winner's rating
    winner_rating = cursor.execute(
        "SELECT rating FROM users WHERE username = ?", (winner,)
    ).fetchone()[0]
    cursor.execute(
        "UPDATE users SET rating = ? WHERE username = ?",
        (winner_rating + winner_mod, winner),
    )
    # Setting loser's rating
    loser_rating = cursor.execute(
        "SELECT rating FROM users WHERE username = ?", (loser,)
    ).fetchone()[0]

    # if loser's rating is below 100 (min)
    if loser_rating - loser_mod < 100:
        # set it to 100
        cursor.execute("UPDATE users SET rating = ? WHERE username = ?", (100, loser)),
    # else
    else:
        # Deduct as normal
        cursor.execute(
            "UPDATE users SET rating = ? WHERE username = ?",
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
    users = sqlite3.connect(db)
    cursor = users.cursor()
    # Getting pfps
    white_pfp = (
        "/static/img/pfp/"
        + cursor.execute(
            "SELECT pfp FROM users WHERE username = ?", (session["curr_game"]["white"],)
        ).fetchone()[0]
    )
    black_pfp = (
        "/static/img/pfp/"
        + cursor.execute(
            "SELECT pfp FROM users WHERE username = ?", (session["curr_game"]["black"],)
        ).fetchone()[0]
    )
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
        return render_template("play.html")
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
            (time, rated, session["username"]),
        )
        # Turning into a dict object
        pending_games = [dict(row) for row in pending_games]

        # If pending games available
        if len(pending_games) >= 1:
            # Add user to as black and set staus to ongoing
            cursor.execute(
                "UPDATE ksgame SET black = ?, status = 'ongoing', black_rating = ? WHERE game_id = ?",
                (session["username"], rating, pending_games[0]["game_id"]),
            )
            # Commit
            games.commit()
            # Getting current game info
            curr_game = cursor.execute(
                "SELECT * FROM ksgame WHERE game_id = ?", (pending_games[0]["game_id"],)
            )
            curr_game = [dict(row) for row in curr_game][0]

            # Saving to cookie session
            session["curr_game"] = curr_game
            # # Redirect to play/ {gameid of the game}
            return redirect("/play/" + str(pending_games[0]["game_id"]))
        # If no pending available
        else:
            # Adding user as white if no pending available, and adding the game params with it
            cursor.execute(
                "INSERT INTO ksgame (white, status, time, rated, white_rating) VALUES (?,?,?,?,?)",
                (session["username"], "searching", time, rated, rating),
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

            # Saving to cookie session
            session["curr_game"] = curr_game
            # Redirecting to their game url

            return redirect("/play/" + str(cursor.lastrowid))
