from flask import Blueprint
import sqlite3
from flask import render_template, request

db = "games.db"
searches = Blueprint("searches", __name__)

# Search Page
@searches.route("/search", methods=["POST", "GET"])
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
@searches.route("/openings", methods=["GET", "POST"])
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
