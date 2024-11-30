from flask import session, request, render_template, Flask, url_for, redirect, flash
from livereload import Server
from helpers import get_game_data, insert_game_in_db, get_db_connection, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
from sqlite3 import connect

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key_for_dev_only")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Path to games and database connection
game_path = 'static/games'
db = get_db_connection()

# ------------------------- Routes -------------------------


@app.route('/login', methods=("GET", "POST"))
def login():
    if (request.method == "POST"):
        username = request.form.get("username") 
        password = request.form.get("password")

        if not username or not password:
            flash("Make sure to fill out the the fields")
            return redirect("/login")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if rows is None or not check_password_hash(rows["hash"], password):
            flash ("Invalid username and/or password")
            return redirect("/login")

        session["user_id"] = rows['id']
        
        return redirect("/")

    return render_template("login.html")

@app.route('/register', methods=("GET", "POST"))
def register():
    if (request.method == "POST"):
        username = request.form.get("username") 
        email = request.form.get("email") 
        password = request.form.get("password")
        
        if not username or not email or not password:
            flash("Make sure to fill your infos")
            return render_template("register.html")
        
        usernames_data = db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchall()
        emails_data = db.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchall()
        
        if usernames_data:
            flash("Username already exists!")
            return render_template("register.html")
        
        if emails_data:
            flash("Email already exists!")
            return render_template("register.html")

        if len(password) <= 6:
            flash("Password must contain atleast 7 characters!")
            return render_template("register.html")
        else:   
            hashed_password = generate_password_hash(password)
        
        db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", (username, email, hashed_password))
        db.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
def home():
    # Check if 'user_id' exists in the session
    user_id = session.get('user_id')

    if user_id:
        # Fetch user details if logged in
        user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()

        if user:  # Ensure user exists in the database
            username = user[0]
            coins = user[1]
        else:
            # Handle case where user_id is invalid (e.g., user was deleted)
            session.pop('user_id', None)
            return redirect('/login')  # Or render a guest template
    else:
        # Handle non-logged-in user
        username = None
        coins = None

    # Getting featured games with a random selection
    featured_games = db.execute("SELECT * FROM games ORDER BY RANDOM() LIMIT 6").fetchall()
    # Getting all unique categories
    categories = [row[0] for row in db.execute("SELECT DISTINCT category FROM games").fetchall()]

    # Building a dictionary of category -> games
    category_games = {}
    for category in categories:
        games = db.execute("SELECT * FROM games WHERE category = ?", (category,)).fetchall()
        category_games[category] = games

    return render_template("home.html", username=username, coins=coins, featured_games=featured_games, categories=categories, game=game ,category_games=category_games)

@app.route("/search", methods=['GET', 'POST'])
def search():
    user_id = session["user_id"]
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        username = user[0]
        coins = user[1]

    if (request.method == 'POST'):
        check_game = request.form.get("search")

        searched_games = db.execute("SELECT * FROM games WHERE title LIKE ? ", (f'{check_game}%',)).fetchall()

    return render_template("search.html", searched_games=searched_games, check_game=check_game, username=username, coins=coins)

@app.route("/favorites")
@login_required
def favorites():
    
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        username = user[0]
        coins = user[1]

    favorite_games = db.execute("SELECT * FROM games JOIN favorites on games.id = favorites.game_id WHERE favorites.user_id = ? ", (user_id,)).fetchall()

    return render_template("favorites.html", favorite_games=favorite_games, username=username, coins=coins)

@app.route("/shop")
@login_required
def shop():
    insert_game_in_db(get_game_data(game_path))  # Insert game data into the DB
    games_data = db.execute("SELECT * FROM games").fetchall()  
    
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        username = user[0]
        coins = user[1]

    return render_template("shop.html", games_data=games_data, username=username, coins=coins)


@app.route("/library")
@login_required
def library():
    user_id = session['user_id']
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]    

    games_owned = db.execute("SELECT * FROM games JOIN transactions on games.id = transactions.game_id WHERE transactions.user_id = ? ORDER BY games.title", (user_id,)).fetchall()
    
    return render_template ("library.html", username=username, coins=coins, games_owned = games_owned) 

@app.route("/<title>", methods=["GET", "POST"])
@login_required
def game(title):
    user_id = session['user_id']
    
    # Exclude the current game from featured games
    game = db.execute("SELECT * FROM games WHERE title = ?", (title,)).fetchone()
   
    game_id = game['id']
    featured_games = db.execute("SELECT * FROM games WHERE id != ? ORDER BY RANDOM() LIMIT 6", (game_id,)).fetchall()
    
    # Get user info
    user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user[0]
    coins = user[1]
    game_price = game['price']
    
    # Check if the game is owned by the user
    owned = db.execute("SELECT 1 FROM transactions WHERE user_id = ? AND game_id = ?", (user_id, game_id)).fetchone() is not None
    is_favorite = db.execute("SELECT 1 FROM favorites WHERE user_id = ? AND game_id = ?", (user_id, game_id)).fetchone() is not None

    if request.method == "POST":
        # Handle favorite/unfavorite
        if "favorite" in request.form:
            favorite_action = request.form["favorite"]
            if favorite_action == "add" and not is_favorite:
                db.execute("INSERT INTO favorites (user_id, game_id) VALUES (?, ?)", (user_id, game_id))
                flash("Added to favorites!")
                is_favorite = True
            elif favorite_action == "remove" and is_favorite:
                db.execute("DELETE FROM favorites WHERE user_id = ? AND game_id = ?", (user_id, game_id))
                flash("Removed from favorites!")
                is_favorite = False
            db.commit()
            return redirect(url_for("game", title=title))

        # Handle game purchase
        if not owned:
            if coins < game_price:
                flash("Insufficient Flash coins")
                return redirect(url_for("game", title=title))

            new_balance = coins - game_price
            db.execute("INSERT INTO transactions (user_id, game_id) VALUES (?, ?)", (user_id, game_id))
            db.execute("UPDATE users SET coins = ?, game_id = ? WHERE id = ?", (new_balance, game_id, user_id))
            
            coins = new_balance
            owned = True
            flash("Thanks for your purchase")
            db.commit()

    return render_template("game.html", game=game, username=username, coins=coins, featured_games=featured_games, owned=owned, is_favorite=is_favorite)


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