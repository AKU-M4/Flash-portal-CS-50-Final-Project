import os
from sqlite3 import connect, Row

def get_db_connection():
    conn = connect('database.db', check_same_thread = False)
    conn.row_factory = Row  # This makes rows behave like dictionaries
    return conn

def get_game_data(base_path):
    games_data = []
    
    if not os.path.isdir(base_path):
        raise ValueError(f"The path {base_path} is not a directory or does not exist.")
    
    # Looping through the game folder with the given base path
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        if os.path.isdir(folder_path):  # If it's a directory, process it as a game
            
            game_data = {
                "title": folder_name.replace('%20', ''),
                "url": "none",
                "thumbnail": "none",
                "preview": "none",   
                "category": "none",
                "price": "400",
                "description": "none",
            }
            
            # Loop through the files in the game folder
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                
                if file_name.endswith(".swf"):  # Game file
                    game_data["url"] = file_path
                
                elif file_name.endswith(".png") or file_name.endswith(".jpg"):  # Thumbnail image
                    game_data["thumbnail"] = file_path
                
                elif file_name.endswith(".gif"):  # Preview gif
                    game_data["preview"] = file_path
                
                elif file_name == 'category.txt':  # Category file
                    with open(file_path, 'r') as category_file:
                        game_data["category"] = category_file.read().strip()

                elif file_name == 'Description.txt':  # Description file
                    with open(file_path, 'r') as description_file:
                        game_data["description"] = description_file.read().strip()

                elif file_name.isdigit():  # Price file (numeric name)
                    game_data["price"] = int(file_name)

            games_data.append(game_data)
        
    return games_data



def insert_game_in_db(games_data):
    conn = get_db_connection()
    db = conn.cursor()

    for game in games_data:
        #checking if the game data already exists
        existing_game = db.execute("SELECT * FROM games WHERE title = ? ",(game["title"],)).fetchone()  
        
        #if it does't exist we proceed by inserting a new one
        if not existing_game:
            db.execute("INSERT INTO games (title, url, thumbnail, preview, category, price, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        game["title"], game["url"], game["thumbnail"], game["preview"], game["category"], game["price"], game["description"])
        #else update existing entry
        else: 
            db.execute("UPDATE games SET url = ?, thumbnail = ?, preview = ? , category = ?, price = ?, description = ? WHERE title = ?",
                        (game["url"], game["thumbnail"], game["preview"], game["category"], game["price"], game["description"], game["title"]))
    conn.commit()
    conn.close()
