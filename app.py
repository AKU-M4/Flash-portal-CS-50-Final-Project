from flask import session, request, render_template, Flask, url_for, redirect
from livereload import Server
from helpers import get_game_data, insert_game_in_db, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user
import os
from sqlite3 import connect

app = Flask(__name__)

# Adding game_data to insert in our database
game_path = 'static/games'
db = get_db_connection()


@app.route('/login', methods=("GET", "POST"))
def login():
    if (request.method.get == "POST"):
        username = request.form.get("username") 
        password = request.form.get("password")

        if not username or not password:
            flash("Make sure to fill out the blanks")
        
        
        return redirect("/")

    return render_template("login.html")

@app.route('/register', methods=("GET", "POST"))
def register():
    if (request.method.get == "POST"):
        username = request.form.get("username") 
        email = request.form.get("email") 
        password = request.form.get("password")

        if not username or not email or not password:
            flash("Make sure to fill out the blanks")
        

        return redirect("/")

    return render_template("register.html")


@app.route("/", methods=("GET", "POST"))
def home():
    return render_template("home.html")



@app.route("/shop")
def shop():
    insert_game_in_db(get_game_data(game_path))  # Insert game data into the DB
    games_data = db.execute("SELECT * FROM games").fetchall()  
    
    return render_template("shop.html", games_data=games_data)



@app.route("/game/<title>", methods=["GET", "POST"])
def game(title):
    
    game= db.execute("SELECT * FROM games WHERE title = ?", (title,)).fetchone()

    
    return render_template("game.html", game=game)

if __name__ == "__main__":
    app.run(debug=True)

    # Use livereload to auto-reload on code changes
    server = Server(app.wsgi_app)
    server.watch('static/')  # Watches the 'static' folder
    server.watch('templates/')  # Watches the 'templates' folder
    server.serve(port=5000, debug=True)
