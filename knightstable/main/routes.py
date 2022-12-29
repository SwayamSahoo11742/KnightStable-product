from flask import Blueprint
import sqlite3
from flask import render_template, request

db = "games.db"
main = Blueprint("main", __name__)


@main.route("/about")
def about():
    return render_template("about.html")


# Reccomended Page
@main.route("/recommended")
def recommended():
    # This is a static template, therefore only returning template
    return render_template("recommended.html")


@main.route("/members", methods=["GET", "POST"])
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


@main.route("/contact")
def contact():
    return render_template("contact.html")
