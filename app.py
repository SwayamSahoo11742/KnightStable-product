import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import strip_eval, cap, attempt, save_pfp
from flask_socketio import SocketIO, send, join_room
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


# -------------------------------------FLASK ROUTES--------------------------------------------------------------#
# Register Page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # returninf template
        return render_template("register.html")
    else:
        # Connecting to db
        users = sqlite3.connect(db)
        users.row_factory = sqlite3.Row
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

        # Commiting
        users.commit()

        # Setting user's satus as logged
        session["logged"] = True
        user_rows = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()
        # Updating user's session with needed info
        session["user_id"] = user_rows[0]["id"]
        session["username"] = user_rows[0]["username"]
        session["pfp"] = "/static\img\pfp/" + user_rows[0]["pfp"]
        session["about"] = user_rows[0]["about"]
        # Cloding db
        users.close()
        # Flask Message
        flash("Successfully registered")
        return redirect("/")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
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
        session["pfp"] = "/static\img\pfp/" + user_rows[0]["pfp"]
        session["about"] = user_rows[0]["about"]
        flash("Logged in Successfully")
        return redirect("/")


# Logout page


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logout.html")
    else:
        # Logging user out
        session["logged"] == False
        # Clearing login session
        session.clear()
        return redirect("/about")


# Home page
@app.route("/")
def home():
    # Checking if user is logged
    if "logged" not in session:
        flash("You should log in", "alert-danger")
        return redirect("/about")
    # Connecting to db
    users = sqlite3.connect(db)
    # Row Factory
    users.row_factory = sqlite3.Row
    # Cursor object
    cursor = users.cursor()

    # Recent Games
    games = cursor.execute("SELECT white, black, result, pgn FROM ksgame WHERE white = ? OR black = ? ORDER BY datetime DESC LIMIT 5", (session["username"], session["username"]))
    games = [dict(x) for x in games]
    
    # Rating 
    rating = dict(cursor.execute("SELECT rating FROM users WHERE username = ?", (session["username"],)).fetchone())["rating"]

    # Rending template
    return render_template("home.html", games=games, rating=rating)

# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Search Page
@app.route("/search", methods=["POST", "GET"])
def search():
    # If get render template
    if request.method == "GET":

        return render_template("search.html")
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
            return render_template("search.html", games=result)
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
        return render_template("openings.html")
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
            openings=openings,
            color=color.capitalize(),
            moves=moves,
            name=name.capitalize(),
        )


# Reccomended Page
@app.route("/recommended")
def recommended():
    # This is a static template, therefore only returning template
    return render_template("recommended.html")


# Page where the game playing will be commenced
# Dynamic to support different rooms
@app.route("/play/<id>")
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
@app.route("/play", methods=["POST", "GET"])
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


# Profile Page
@app.route("/profile", methods=["GET", "POST"])
def profile():
    # If Just visiting
    if request.method == "GET":
        # Return the template
        return render_template("profile.html")
    # If changes applied
    else:
        # Get about text
        about = request.form.get("about")
        # update session
        session["about"] = about
        # COnnect to db
        users = sqlite3.connect(db)
        cursor = users.cursor()
        # Update db
        cursor.execute(
            "UPDATE users SET about = ? WHERE id = ?", (about, session["user_id"])
        )
        # Commit changes
        users.commit()
        # Flask Success message
        flash("Changes Saved")
        # Close db
        users.close()
        # Redirect to same page
        return redirect("/profile")


# Account settings page
@app.route("/account", methods=["GET", "POST"])
def account():
    # IF get
    if request.method == "GET":
        # Render
        return render_template("account.html")
    else:
        # Connect to db
        users = sqlite3.connect(db)
        # Cursor object
        cursor = users.cursor()

        # If pfp change
        if request.form.get("submit") == "pfp-change":
            # Get pfp file
            pfp = request.files.get("pfp")
            # Save it
            pfp_file = save_pfp(pfp, app)
            # Update db
            cursor.execute(
                "UPDATE users SET pfp = ? WHERE id = ?", (pfp_file, session["user_id"])
            )
            # Update Session
            session["pfp"] = "static\img\pfp/" + pfp_file

            # Commiting changes
            users.commit()

            # Closing db
            users.close()

            # Redirect back
            flash("Profile Picture Updated", "alert-success")
            return redirect("/account")

        # If username change
        if request.form.get("submit") == "name-change":
            # Checking Passwords
            # Getting inpted password
            password = request.form.get("password")
            # Getting real password
            selfpass = cursor.execute(
                "SELECT hash FROM users WHERE id = ?", (session["user_id"],)
            ).fetchone()[0]

            # IF passwords did not match
            if not check_password_hash(selfpass, password):
                # close db, Send message and redirect
                users.close()
                flash("Password incorrect", "alert-danger")
                return redirect("/account")
            # If password Matched
            else:
                # Update session
                session["username"] = request.form.get("username")

                # Update db
                cursor.execute(
                    "UPDATE users SET username = ? WHERE id = ?",
                    (request.form.get("username"), session["user_id"]),
                )

                # Commit changes
                users.commit()

                # Close db
                users.close()

                # Flash success message
                flash("Changed Applied", "alert-success")
                # redirect
                return redirect("/account")

        # If password change
        if request.form.get("submit") == "pass-change":
            # Get passwords
            # Getting inputed password
            password = request.form.get("current-password")
            # Getting real password
            selfpass = cursor.execute(
                "SELECT hash FROM users WHERE id = ?", (session["user_id"],)
            ).fetchone()[0]

            # IF passwords did not match
            if not check_password_hash(selfpass, password):
                # Close db
                users.close()
                # Send message and redirect
                flash("Password incorrect", "alert-danger")
                return redirect("/account")
            # If passwords matched
            else:
                # Get the new pass and its confirmation
                new_pass = request.form.get("new-password")
                confirm_pass = request.form.get("confirm-password")

                # If confirmation and new pass match
                if new_pass == confirm_pass:
                    # Generate password hash
                    hashed_pass = generate_password_hash(new_pass)
                    # Update password
                    cursor.execute(
                        "UPDATE users SET hash = ? WHERE id = ?",
                        (hashed_pass, session["user_id"]),
                    )

                    # Commit changes
                    users.commit()
                    # Close db
                    users.close()
                    # Flash message of succession
                    flash("Password changed", "alert-success")
                    # Redirect
                    return redirect("/account")

                # If did not match
                else:
                    # Close db
                    users.close()
                    # Flash message of not succession
                    flash("Password did not match", "alert-danger")
                    # Redirect
                    return redirect("/account")


# Stats Page
@app.route("/user/<name>", methods=["GET", "POST"])
def stat(name):
    # Connect to db
    users = sqlite3.connect(db)
    # Cursor object
    cursor = users.cursor()

    # Checking if user exists
    count = cursor.execute(
        "SELECT COUNT(username) FROM users WHERE username = ?", (name,)
    ).fetchone()[0]
    if count == 0:
        return redirect("/user/" + session["username"])

    # Getting White stats
    w_wins = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE white = ? AND result = ?",
        (name, "1-0"),
    ).fetchone()[0]
    w_loss = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE white = ? AND result = ?",
        (name, "0-1"),
    ).fetchone()[0]
    w_draw = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE white = ? AND result = ?",
        (name, "1-1"),
    ).fetchone()[0]
    white_stats = [w_wins, w_loss, w_draw]

    # Getting Black Stats
    b_wins = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE black = ? AND result = ?",
        (name, "0-1"),
    ).fetchone()[0]
    b_loss = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE black = ? AND result = ?",
        (name, "1-0"),
    ).fetchone()[0]
    b_draw = cursor.execute(
        "SELECT COUNT(game_id) FROM ksgame WHERE black = ? AND result = ?",
        (name, "1-1"),
    ).fetchone()[0]
    black_stats = [b_wins, b_loss, b_draw]

    # Getting all Stats
    all_wins = w_wins + b_wins
    all_loss = w_loss + b_loss
    all_draw = w_draw + b_draw
    all_stats = [all_wins, all_loss, all_draw]

    # Ratng points
    ratings = cursor.execute(
        "SELECT (CASE WHEN white = ? THEN white_rating ELSE black_rating END) as rating FROM ksgame WHERE black = ? OR white = ? ORDER BY datetime;",
        (name, name, name),
    ).fetchall()
    ratings = [x[0] for x in ratings]
    if ratings == []:
        ratings = [100]

    # Getting about text
    about = cursor.execute(
        "SELECT about FROM users WHERE username = ?", (name,)
    ).fetchone()[0]

    # Getting games
    games = cursor.execute(
        "SELECT white, black, result, pgn FROM ksgame WHERE black = ? OR white = ? LIMIT 10",
        (name, name),
    ).fetchall()
    # Closing db
    users.close()

    return render_template(
        "stat.html",
        name=name,
        white_stats=white_stats,
        black_stats=black_stats,
        all_stats=all_stats,
        ratings=ratings,
        current_rating=ratings[len(ratings) - 1],
        about=about,
        games=games,
    )


@app.route("/members", methods=["GET", "POST"])
def members():
    # If GET request
    if request.method == "GET":
        # Connecting to db
        members = sqlite3.connect(db)
        members.row_factory = sqlite3.Row
        # Cursor object
        cursor = members.cursor()

        # Getting top 10 players
        users = cursor.execute(
            "SELECT username, rating FROM users ORDER BY rating DESC LIMIT 10"
        ).fetchall()
        users = [dict(x) for x in users]

        members.close()
        # Return template
        return render_template("members.html", users=users)
    # If Post request
    else:
        username = request.form.get("username")
        # Connecting to db
        members = sqlite3.connect(db)
        members.row_factory = sqlite3.Row
        # Cursor object
        cursor = members.cursor()

        # Getting top 10 players
        users = cursor.execute(
            "SELECT username, rating FROM users WHERE username LIKE ?",
            ("%" + username + "%",),
        ).fetchall()
        users = [dict(x) for x in users]

        # Closing db
        members.close()
        return render_template("members.html", users=users)


if __name__ == "__main__":
    socketio.run(app)
