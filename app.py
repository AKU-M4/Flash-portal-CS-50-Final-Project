from flask import session, request, render_template, Flask, url_for, redirect
from flask_session import Session
from livereload import Server
from helpers import get_game_data, insert_game_in_db
import os
import sqlite3

app = Flask(__name__)

db = sqlite3.connect("database.db")


#adding game_data to instert in our database
game_path = 'static/games'

@app.route("/", methods=("GET", "POST"))
def home():
    

    return render_template("home.html")

@app.route("/shop")
def shop():
    games_data = get_game_data(game_path)
    
    return render_template("shop.html", games_data=games_data)


@app.route("/{{ game['title'] }}")
def game():

    return render_template ("game.html",  )


if (__name__)=="__main__":
    app.run(debug=True)

    # Use livereload to auto-reload on code changes
    server = Server(app.wsgi_app)
    server.watch('static/')       # Watches the 'static' folder
    server.watch('templates/')    # Watches the 'templates' folder
    server.serve(port=5000, debug=True)
