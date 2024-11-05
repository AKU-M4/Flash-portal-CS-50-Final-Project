from flask import Flask, session, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from helpers import (
    get_game_data, 
    insert_game_in_db, 
    purchase_game,
    Game,
    Base,
    engine,
    Session as DBSession
)
import os
import sqlalchemy as sa

app = Flask(__name__)
app.secret_key = 'chlayad w nod nayad'  # Consider moving this to environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define User model to match your SQL schema
class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(20), nullable=False)
    email = sa.Column(sa.String(60), nullable=False)
    hash = sa.Column(sa.Text, nullable=False)
    coins = sa.Column(sa.Numeric, default=1000.00)
    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'), nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'), nullable=False)
# Create all tables
Base.metadata.create_all(engine)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        db_session = DBSession()
        
        user = db_session.query(User).filter_by(
            username=request.form.get("username")
        ).first()
        
        if user and check_password_hash(user.hash, request.form.get("password")):
            session["user_id"] = user.id
            db_session.close()
            return redirect("/")
        
        db_session.close()
        flash("Invalid username and/or password")
        return redirect("/login")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db_session = DBSession()
        
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not username or not email or not password:
            flash("Please fill all fields")
            return redirect("/register")
            
        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return redirect("/register")
            
        new_user = User(
            username=username,
            email=email,
            hash=generate_password_hash(password),
            game_id=1 
        )
        
        db_session.add(new_user)
        db_session.commit()
        db_session.close()
        
        flash("Registered successfully!")
        return redirect("/login")
        
    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    db_session = DBSession()
    user = db_session.query(User).get(session["user_id"])
    db_session.close()
    return render_template("home.html", user=user)

@app.route("/shop")
@login_required
def shop():
    games_data = get_game_data(os.path.join(app.static_folder, 'games'))
    # Insert games into database
    insert_game_in_db(games_data)
    
    db_session = DBSession()
    games = db_session.query(Game).all()
    db_session.close()
    
    return render_template("shop.html", games_data=games)

@app.route("/game/<title>", methods=["GET", "POST"])
@login_required
def game(title):
    db_session = DBSession()
    game = db_session.query(Game).filter_by(title=title).first()
    
    if not game:
        flash("Game not found")
        return redirect("/shop")
    
    if request.method == "POST":
        result = purchase_game(session["user_id"], game.id)
        flash(result)
        return redirect("/shop")
    
    # Check if user has already purchased the game
    transaction = db_session.query(Transaction).filter_by(
    user_id=session["user_id"],
    game_id=game.id
    ).first()
    
    user = db_session.query(User).get(session["user_id"])
    can_purchase = user.coins >= game.price if user else False
    
    db_session.close()
    
    return render_template(
        "game.html",
        game=game,
        owned=transaction is not None,
        can_purchase=can_purchase
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)