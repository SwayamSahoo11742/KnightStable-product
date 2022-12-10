import os 
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import strip_eval, cap, attempt

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connecting to database
db = "C:/Users/Dodo/Desktop/Projects/games.db"

# Adding custom functions
app.jinja_env.globals.update(strip_eval=strip_eval)
app.jinja_env.globals.update(cap=cap)


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # returninf template
        return render_template("register.html", logged=attempt(session,"logged"))
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
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", logged=attempt(session,"logged"))
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
        user_rows = cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        if len(user_rows) != 1 or not check_password_hash(user_rows[0]["hash"], request.form.get("password")):
            flash("Password and Username did not match", "error")
            return redirect("/login")
        
        # Setting user id and logged status to true
        session["user_id"] = user_rows[0]["id"]
        session["logged"] = True
        flash("Logged in Successfully")
        return redirect("/")

# Logout page
@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logout.html", logged=attempt(session,"logged"))
    else:
        # Logging user out
        session["logged"] == False
        # Clearing login session
        session.clear()
        return redirect("/")

# Home page
@app.route("/")
def home():
    return render_template("index.html", logged=attempt(session,"logged"))


# Search Page
@app.route("/search", methods=["POST","GET"])
def search():
    # If get render template
    if request.method == "GET":

        return render_template("search.html", logged=attempt(session,"logged"))
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
            data_tuple = ("%"+black_user+"%", "%"+white_user+"%", "%"+moves+"%", "%"+opening+"%", max_rating, min_rating, result)
            
            valid_games = cursor.execute(query, data_tuple)
            
            # Making a list of dictionaries with the game data
            result = [dict(row) for row in valid_games]
            
            cursor.close()
            return render_template("search.html", games=result, logged=attempt(session,"logged"))
        else:
            # Defining Query
            query = "SELECT * FROM games WHERE black LIKE ? AND white LIKE ? AND moves LIKE ? AND opening LIKE ? AND white_elo <= ? AND white_elo >= ? LIMIT(50)"
            
            # Creating a tuple for the values that will go into the query
            data_tuple = ("%"+black_user+"%", "%"+white_user+"%", "%"+moves+"%", "%"+opening+"%", max_rating, min_rating)
            
            valid_games = cursor.execute(query, data_tuple)
            
            # Making a list of dictionaries with the game data
            results = [dict(row) for row in valid_games]
            
            cursor.close()
            return render_template("search.html",logged=attempt(session,"logged"), games=results, black_user=black_user, white_user=white_user, result=result, max_rating=max_rating, min_rating=min_rating, moves=moves, opening=opening)


# Opening search
@app.route("/openings", methods=["GET", "POST"])
def openings():
    if request.method == "GET":
        return render_template("openings.html", logged=attempt(session,"logged"))
    else:
        games = sqlite3.connect(db)
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
            return render_template("openings.html", openings=openings, color=color.capitalize(), moves=moves, name=name.capitalize(),logged=attempt(session,"logged"))
        else:
            name = request.form.get("opening")
            moves = request.form.get("moves")
            print(color)
            query = "SELECT * FROM opening WHERE name LIKE ? AND moves LIKE ?"
            data_tuple = ("%"+name+"%", "%"+moves+"%")
            buffer = cursor.execute(query,data_tuple)
            openings = [dict(row) for row in buffer]
            cursor.close()
            return render_template("openings.html",logged=attempt(session,"logged"), openings=openings, color=color.capitalize(), moves=moves, name=name.capitalize())


# Reccomended Page
@app.route("/recommended")
def recommended():
    return render_template("recommended.html", logged=attempt(session,"logged"))


@app.route("/play")
def play():
    return render_template("play.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)