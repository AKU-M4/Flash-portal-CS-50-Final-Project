from flask import Flask, session, request, render_template, url_for, redirect, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import connect
import os
from helpers import get_game_data, insert_game_in_db, get_db_connection, login_required

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key_for_dev_only")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Path to games and database connection
game_path = 'static/games'
db = get_db_connection()

# ------------------------- Routes -------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please fill out all fields")
            return redirect("/login")

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password")
            return redirect("/login")

        session["user_id"] = user['id']
        return redirect("/")

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("Please complete all fields")
            return render_template("register.html")

        if len(password) < 7:
            flash("Password must be at least 7 characters long")
            return render_template("register.html")

        if db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone():
            flash("Username already exists")
            return render_template("register.html")

        if db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone():
            flash("Email already registered")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hashed_password))
        db.commit()

        flash("Registered successfully. Please log in.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
def home():
    user_id = session.get("user_id")

    if user_id:
        user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            username, coins = user["username"], user["coins"]
        else:
            session.pop("user_id", None)
            return redirect("/login")
    else:
        username, coins = None, None

    featured_games = db.execute("SELECT * FROM games ORDER BY RANDOM() LIMIT 6").fetchall()
    categories = [row[0] for row in db.execute("SELECT DISTINCT category FROM games").fetchall()]

    category_games = {
        category: db.execute("SELECT * FROM games WHERE category = ?", (category,)).fetchall()
        for category in categories
    }

    return render_template("home.html", username=username, coins=coins, featured_games=featured_games, categories=categories, category_games=category_games)


@app.route("/search", methods=["POST"])
@login_required
def search():
    user_id = session["user_id"]
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

    if user:
        username, coins = user["username"], user["coins"]

    search_query = request.form.get("search")
    searched_games = db.execute("SELECT * FROM games WHERE title LIKE ?", (f"%{search_query}%",)).fetchall()

    return render_template("search.html", searched_games=searched_games, username=username, coins=coins)


@app.route("/favorites")
@login_required
def favorites():
    user_id = session["user_id"]
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

    username, coins = user["username"], user["coins"]
    favorite_games = db.execute(
        "SELECT * FROM games JOIN favorites ON games.id = favorites.game_id WHERE favorites.user_id = ?", (user_id,)
    ).fetchall()

    return render_template("favorites.html", favorite_games=favorite_games, username=username, coins=coins)


@app.route("/shop")
@login_required
def shop():
    insert_game_in_db(get_game_data(game_path))  # Insert game data
    games = db.execute("SELECT * FROM games").fetchall()

    user_id = session["user_id"]
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

    username, coins = user["username"], user["coins"]
    return render_template("shop.html", games_data=games, username=username, coins=coins)


@app.route("/<title>", methods=["GET", "POST"])
@login_required
def game(title):
    user_id = session["user_id"]
    game = db.execute("SELECT * FROM games WHERE title = ?", (title,)).fetchone()

    if not game:
        flash("Game not found")
        return redirect("/")

    game_id = game["id"]
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username, coins = user["username"], user["coins"]

    owned = db.execute("SELECT 1 FROM transactions WHERE user_id = ? AND game_id = ?", (user_id, game_id)).fetchone()
    is_favorite = db.execute("SELECT 1 FROM favorites WHERE user_id = ? AND game_id = ?", (user_id, game_id)).fetchone()

    if request.method == "POST":
        if "favorite" in request.form:
            action = request.form["favorite"]
            if action == "add" and not is_favorite:
                db.execute("INSERT INTO favorites (user_id, game_id) VALUES (?, ?)", (user_id, game_id))
            elif action == "remove" and is_favorite:
                db.execute("DELETE FROM favorites WHERE user_id = ? AND game_id = ?", (user_id, game_id))
            db.commit()
            return redirect(url_for("game", title=title))

        if not owned:
            if coins < game["price"]:
                flash("Not enough coins to purchase this game")
                return redirect(url_for("game", title=title))

            db.execute("INSERT INTO transactions (user_id, game_id) VALUES (?, ?)", (user_id, game_id))
            db.execute("UPDATE users SET coins = ? WHERE id = ?", (coins - game["price"], user_id))
            db.commit()

    return render_template("game.html", game=game, username=username, coins=coins, owned=owned, is_favorite=is_favorite)


@app.route("/Action")
@login_required
def Action():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Action'").fetchall()

    return render_template("Action.html", games=games, username=username, coins=coins)

@app.route("/Adventure")
@login_required
def Adventure():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Adventure'").fetchall()

    return render_template("Adventure.html", games=games, username=username, coins=coins)

@app.route("/Fighting")
@login_required
def Fighting():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Fighting'").fetchall()

    return render_template("Fighting.html", games=games, username=username, coins=coins)

@app.route("/Horror")
@login_required
def Horror():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Horror'").fetchall()

    return render_template("Horror.html", games=games, username=username, coins=coins)

@app.route("/Puzzle")
@login_required
def Puzzle():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Puzzle'").fetchall()

    return render_template("Puzzle.html", games=games, username=username, coins=coins)

@app.route("/Sports")
@login_required
def Sports():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    
    games = db.execute("SELECT * FROM games WHERE category = 'Sports'").fetchall()

    return render_template("Sports.html", games=games, username=username, coins=coins)

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    user_id = session["user_id"]

    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

    if user:
        username = user[0]
        coins = user[1]

    if (request.method == 'POST'):
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        db.execute("INSERT INTO contacts (name, email, message) VALUES(?, ?, ?)", (name, email, message))
        db.commit()
        
        return redirect("/")
    return render_template("contact.html", username=username, coins=coins)


@app.route("/about", methods=("GET", "POST"))
@login_required
def about():
    user_id = session["user_id"]

    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

    if user:
        username = user[0]
        coins = user[1]

    if (request.method == "POST"):
        feedback = request.form.get("feedack")

        if feedback:
            db.execute("INSERT into feedbacks (feedback) VALUES (?)",(feedback))
            db.commit()
            flash("We appreciate your feedback, Thank you!!")
            return redirect("about.html")
        elif feedback.len() <= 5:
            flash("Invalid feedback, would you please try again.")

    return render_template("about.html", username=username, coins=coins)


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
    # Use livereload to auto-reload on code changes
    server = Server(app.wsgi_app)
    server.watch('static/')  # Watches the 'static' folder
    server.watch('templates/')  # Watches the 'templates' folder
    server.serve(host ='0.0.0.0', port=5000, debug=True)