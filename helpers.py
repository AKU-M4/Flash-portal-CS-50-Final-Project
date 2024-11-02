import os
import sqlite3

db = sqlite3.connect("database.db")

def get_game_data(base_path):
    games_data=[]
    
    if not os.path.isdir(base_path):
        raise ValueError(f"the path {base_path} is not a directory or does not exist.")
    
    #looping through the game with the given game path
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        if os.path.isdir(folder_path):
            
            game_data = {
                "title": folder_name.replace('%20', ''),
                "url": "none",
                "thumbnail": "none",
                "preview": "none",   
                "category": "none",
                "price": "none",
            }
            
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith(".swf"):
                game_data["url"] = file_path
            
            elif file_name.endswith(".png") or file_name.endswith(".jpg"):
                game_data["thumbnail"] = file_path
            elif file_name.endswith(".mp4"):
                game_data["preview"] = file_path
            elif file_name.endswith(".txt"):
               game_data["category"] = file_name.replace(".txt" , "")
            elif file_name.isdigit():
                game_data["price"] = file_name
            games_data.append(game_data)
        
    return games_data



def insert_game_in_db(games_data):
    for game in games_data:
        #checking if the game data already exists
        existing_game = db.execute("SELECT * FROM games WHERE title = ? ",(game["title"])).fetchone()  
        
        #if it does't exist we proceed by inserting a new one
        if not existing_game:
            db.execute("INSERT INTO games (title, url, thumbnail, preview, category, price) VALUES (?, ?, ?, ?, ?, ?)",
                        game["title"], game["url"], game["thumbnail"], game["preview"], game["category"], game["price"])
        #else we update it
        else: 
            db.execute("UPDATE games SET url = ?, thumbnail = ?, preview = ? , category = ?, price = ?, WHERE title = ?)",
                        game["url"], game["thumbnail"], game["preview"], game["category"], game["price"], game["title"])
    db.commit();


def purchase_game(user_id, game_id):
    # Check if the game exists and the user has enough coins
    game = db.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    user = db.execute("SELECT coins FROM users WHERE id = ?", (user_id,)).fetchone()

    if not game:
        return "Game not found."
    if user['coins'] < game['price']:
        return "Not enough flash coins to purchase this game."

    # Insert into transactions
    db.execute("INSERT INTO transactions (user_id, game_id) VALUES (?, ?)", (user_id, game_id))

    # Deduct coins from the user
    db.execute("UPDATE usersSET coins = coins - ? WHERE id = ?", (game['price'], user_id))
    return "Purchase successful!"

