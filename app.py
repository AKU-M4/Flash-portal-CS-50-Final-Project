from flask import session, request, render_template, Flask, url_for, redirect, flash
from livereload import Server
from helpers import get_game_data, insert_game_in_db, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user
from flask_session import Session
import os
from sqlite3 import connect

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key_for_dev_only")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Adding game_data to insert in our database
game_path = 'static/games'
db = get_db_connection()


@app.route('/login', methods=("GET", "POST"))
def login():
    if (request.method == "POST"):
        username = request.form.get("username") 
        password = request.form.get("password")

        if not username or not password:
            flash("Make sure to fill out the the fields")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if rows is None or not check_password_hash(rows["hash"], password):
            flash ("Invalid username and/or password")

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
            hashed_passowrd = generate_password_hash(password)
        
        db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", (username, email, hashed_passowrd))
        db.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/", methods=("GET", "POST"))
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = db.execute("SELECT username, coins FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            username = user[0]
            coins = user[1]
        else:
            username = None
            coins = None
    else:
        username = None
        coins = None

    return render_template("home.html", username=username, coins=coins)


@app.route("/shop")
def shop():
    insert_game_in_db(get_game_data(game_path))  # Insert game data into the DB
    games_data = db.execute("SELECT * FROM games").fetchall()  
    
    return render_template("shop.html", games_data=games_data)



@app.route("/game/<title>", methods=["GET", "POST"])

def game(title):
    
    game= db.execute("SELECT * FROM games WHERE title = ?", (title,)).fetchone()

    
    return render_template("game.html", game=game)

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
    server.serve(port=5000, debug=True)



