import os
import sqlite3
from urllib.parse import unquote
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()

# Setup SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
engine = sa.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define Game Model
class Game(Base):
    __tablename__ = 'games'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(100), unique=True, nullable=False)
    url = sa.Column(sa.String(255), nullable=False)
    thumbnail = sa.Column(sa.String(255), nullable=False)
    preview = sa.Column(sa.String(255))
    category = sa.Column(sa.Text, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    description = sa.Column(sa.Text, nullable=False)  # Added description column

# Extract game data from directory
def get_game_data(base_path):
    games_data = []
    
    if not os.path.isdir(base_path):
        raise ValueError(f"The path {base_path} is not a directory or does not exist.")
    
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        
        if os.path.isdir(folder_path):
            game_data = {
                "title": unquote(folder_name),
                "url": None,
                "thumbnail": None,
                "preview": None,
                "category": "Uncategorized",  # Default category
                "price": 400,
                "description": None
            }
            
            # Ensure paths are relative to static folder
            static_prefix = folder_name + '/'
            
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(static_prefix, file_name)
                abs_file_path = os.path.join(folder_path, file_name)
                
                if file_name.endswith(".swf"):
                    game_data["url"] = file_path
                elif file_name.endswith((".png", ".jpg")):
                    game_data["thumbnail"] = file_path
                elif file_name.endswith(".gif"):
                    game_data["preview"] = file_path
                elif file_name == "description.txt":
                    try:
                        with open(abs_file_path, 'r', encoding='utf-8') as file:
                            game_data["description"] = file.read().strip()
                    except Exception as e:
                        print(f"Error reading description for {folder_name}: {e}")
                elif file_name == "category.txt":
                    try:
                        with open(abs_file_path, 'r', encoding='utf-8') as file:
                            game_data["category"] = file.read().strip()
                    except Exception as e:
                        print(f"Error reading category for {folder_name}: {e}")
                elif file_name.isdigit():
                    game_data["price"] = int(file_name)
            
            # Only add game if required fields are present
            if game_data["url"] and game_data["thumbnail"]:
                games_data.append(game_data)
            else:
                print(f"Skipping {folder_name} due to missing required files")
    
    return games_data

# Insert or update game data in database
def insert_game_in_db(games_data):
    session = Session()
    try:
        for game_data in games_data:
            game = session.query(Game).filter_by(title=game_data["title"]).first()
            
            if not game:
                game = Game(**game_data)
                session.add(game)
            else:
                for key, value in game_data.items():
                    if hasattr(game, key):
                        setattr(game, key, value)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Purchase game with improved error handling
def purchase_game(user_id, game_id):
    session = Session()
    try:
        # Start transaction
        game = session.query(Game).filter_by(id=game_id).first()
        if not game:
            return "Game not found."
        
        # Check if user already owns the game
        existing_transaction = session.execute(
            "SELECT 1 FROM transactions WHERE user_id = :uid AND game_id = :gid",
            {'uid': user_id, 'gid': game_id}
        ).fetchone()
        
        if existing_transaction:
            return "You already own this game!"
        
        # Get user's coins
        user = session.execute(
            "SELECT coins FROM users WHERE id = :id",
            {'id': user_id}
        ).fetchone()
        
        if not user:
            return "User not found."
        
        if user['coins'] < game.price:
            return "Not enough coins to purchase this game."
        
        # Record transaction and update user's coins
        session.execute(
            """INSERT INTO transactions (user_id, game_id, purchase_date) 
               VALUES (:user_id, :game_id, :date)""",
            {
                'user_id': user_id,
                'game_id': game_id,
                'date': datetime.now()
            }
        )
        
        session.execute(
            "UPDATE users SET coins = coins - :price WHERE id = :user_id",
            {'price': game.price, 'user_id': user_id}
        )
        
        # Add to user_games table
        session.execute(
            "INSERT INTO user_games (user_id, game_id) VALUES (:user_id, :game_id)",
            {'user_id': user_id, 'game_id': game_id}
        )
        
        session.commit()
        return "Purchase successful!"
        
    except Exception as e:
        session.rollback()
        return f"An error occurred: {str(e)}"
    finally:
        session.close()

# Initialize database
Base.metadata.create_all(engine)