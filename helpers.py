from functools import wraps
import os
from sqlite3 import connect, Row
from flask import session, redirect, render_template

# Function to establish a connection to the database
def get_db_connection():
    # Connect to the SQLite database (disabling thread checking for Flask's multithreading)
    conn = connect('database.db', check_same_thread=False)
    # Enable row access via dictionary-like keys for easier access to columns
    conn.row_factory = Row
    return conn

# Function to gather game data from directories
def get_game_data(base_path):
    games_data = []  # List to store information about all games
    
    # Validate that the base path is a directory
    if not os.path.isdir(base_path):
        raise ValueError(f"The path {base_path} is not a directory or does not exist.")
    
    # Iterate through all subfolders in the base path
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        # Process only directories
        if os.path.isdir(folder_path):
            # Initialize default game data structure
            game_data = {
                "title": folder_name.replace('%20', ''),  # Decode URL-like folder names
                "url": "none",  # Default for the game URL (SWF file)
                "thumbnail": "none",  # Default for thumbnail image
                "preview": "none",  # Default for preview GIF
                "category": "none",  # Default for game category
                "price": "400",  # Default price
                "description": "none",  # Default description
            }
            
            # Iterate through files in the current game folder
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                
                # Assign file paths or content based on file type
                if file_name.endswith(".swf"):  # Identify the game file
                    game_data["url"] = file_path
                elif file_name.endswith(".png") or file_name.endswith(".jpg"):  # Identify the thumbnail
                    game_data["thumbnail"] = file_path
                elif file_name.endswith(".gif"):  # Identify the preview animation
                    game_data["preview"] = file_path
                elif file_name == 'category.txt':  # Read category from text file
                    with open(file_path, 'r') as category_file:
                        game_data["category"] = category_file.read().strip()
                elif file_name == 'Description.txt':  # Read description from text file
                    with open(file_path, 'r') as description_file:
                        game_data["description"] = description_file.read().strip()
                elif file_name.isdigit():  # Treat numeric filenames as the game price
                    game_data["price"] = int(file_name)

            # Append processed game data to the games list
            games_data.append(game_data)
        
    return games_data  # Return the list of game data dictionaries

# Function to insert or update game data in the database
def insert_game_in_db(games_data):
    conn = get_db_connection()  # Get a database connection
    db = conn.cursor()  # Get a cursor for executing SQL queries

    for game in games_data:
        # Check if a game with the same title already exists
        existing_game = db.execute(
            "SELECT * FROM games WHERE title = ?",
            (game["title"],)
        ).fetchone()
        
        # If the game does not exist, insert it into the database
        if not existing_game:
            db.execute(
                "INSERT INTO games (title, url, thumbnail, preview, category, price, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (game["title"], game["url"], game["thumbnail"], game["preview"], game["category"], game["price"], game["description"])
            )
        # If the game exists, update its details
        else:
            db.execute(
                "UPDATE games SET url = ?, thumbnail = ?, preview = ?, category = ?, price = ?, description = ? WHERE title = ?",
                (game["url"], game["thumbnail"], game["preview"], game["category"], game["price"], game["description"], game["title"])
            )
    
    conn.commit()  # Save changes to the database
    conn.close()  # Close the database connection

# Decorator to enforce user login for certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Redirect to the login page if the user is not logged in
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)  # Call the original function if logged in
    return decorated_function