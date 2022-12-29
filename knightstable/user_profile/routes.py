from flask import Blueprint
import sqlite3
from flask import flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from knightstable.user_profile.helpers import save_pfp, get_uscf_rating

db = "games.db"
profiling = Blueprint("profiling", __name__)


# Profile Page
@profiling.route("/profile", methods=["GET", "POST"])
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
@profiling.route("/account", methods=["GET", "POST"])
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
            pfp_file = save_pfp(pfp, users)
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

        # USCF connect
        if request.form.get("submit") == "uscf-connect":
            print("USCF CONNECT")
            id = request.form.get("uscf-id")
            # Invalid
            if len(id) != 8:
                flash("Invalid USCF ID")
                return redirect("/account", "alert-danger")
            # If valid
            # insert into db
            cursor.execute(
                "UPDATE users SET uscf = ? WHERE id = ? ", (id, session["user_id"])
            )
            # Close db
            users.commit()
            users.close()
            # Adding uscf to session
            session["uscf"] = id
            session["uscf_rating"] = get_uscf_rating(id)
            flash("Successfully connected to USCF", "alert-success")
            return redirect("/account")


# Stats Page
@profiling.route("/user/<name>", methods=["GET", "POST"])
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
