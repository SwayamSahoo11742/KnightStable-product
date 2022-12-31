from flask import Blueprint
from flask import flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from users.helpers import get_uscf_rating, get_tournaments
import psycopg2
from app import db
from psycopg2.extras import RealDictCursor 
users = Blueprint("users", __name__)


# Register Page
@users.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # returninf template
        return render_template("register.html")
    else:
        # Connecting to db
        users = psycopg2.connect(db,cursor_factory=RealDictCursor)
        cursor = users.cursor()

        # Getting user's input
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        # Setting up and executing query for username search
        query = "SELECT COUNT(username) FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        db_users = cursor.fetchone()["count"]

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
        query = "SELECT COUNT(email) FROM users WHERE email = %s"
        db_emails = cursor.execute(query, (email,))
        db_emails = cursor.fetchone()["count"]
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
        query = "INSERT INTO users (username, email, hash) VALUES (%s,%s,%s)"
        data_tuple = (username, email, hash)
        cursor.execute(query, data_tuple)

        # Commiting
        users.commit()

        # Setting user's satus as logged
        session["logged"] = True
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (request.form.get("username"),)
        )
        user_rows = cursor.fetchall()
        # Updating user's session with needed info
        session["user_id"] = user_rows[0]["id"]
        session["username"] = user_rows[0]["username"]
        session["pfp"] = "/static\img\pfp/" + user_rows[0]["pfp"]
        session["about"] = user_rows[0]["about"]
        session["uscf"] = ""
        session["uscf_rating"] = "(Unrated)"
        # Cloding db
        users.close()
        # Flask Message
        flash("Successfully registered")
        return redirect("/")


# Login page
@users.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        users = psycopg2.connect(db, cursor_factory=RealDictCursor)
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
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (request.form.get("username"),)
        )
        user_rows = cursor.fetchall()
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
        session["uscf"] = (
            lambda: user_rows[0]["uscf"] if user_rows[0]["uscf"] != "" else ""
        )
        if user_rows[0]["uscf"] != "":
            session["uscf"] = user_rows[0]["uscf"]
        else:
            session["uscf"] = ""

        if session["uscf"] != "":
            session["uscf_rating"] = get_uscf_rating(session["uscf"])
        else:
            session["uscf_rating"] = "(Unrated)"
        print("logged")
        flash("Logged in Successfully")
        return redirect("/")


# Logout page
@users.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logout.html")
    else:
        # Logging user out
        session["logged"] == False
        # Clearing login session
        session.clear()
        return redirect("/")


# Home page
@users.route("/home")
def home():
    # Checking if user is logged
    if "logged" not in session:
        flash("You should log in", "alert-danger")
        return redirect("/about")
    # Connecting to db
    users = psycopg2.connect(db, cursor_factory=RealDictCursor)
    # Cursor object
    cursor = users.cursor()

    # Getting top 10 players
    cursor.execute(
        "SELECT username, rating FROM users ORDER BY rating DESC LIMIT 10"
    )
    games = cursor.fetchall()
    players = [dict(x) for x in games]

    # Rating
    rating = cursor.execute("SELECT rating FROM users WHERE username = %s", (session["username"],)
        )
    rating = dict(cursor.fetchone())["rating"]
    users.close()

    # Getting recent events
    events = get_tournaments(10)

    # Getting uscf rating
    uscf = session["uscf_rating"]
    # Rending template
    return render_template(
        "home.html", players=players, rating=rating, events=events, uscf=uscf
    )
