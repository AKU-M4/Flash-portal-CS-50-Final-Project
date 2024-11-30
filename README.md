# **🎮 Flash Portal**  

*Your gateway to nostalgic gaming.* 

![Flash Portal Banner](https://github.com/user-attachments/assets/b9aa8851-d2e9-4f49-9229-26ed43ee3edd)


---



## **🌟 About the Project**  

Flash Portal is a web application that revives the charm of classic Flash games. Users can:  
- Play curated games directly on the platform.  
- Track their progress and earn points.  
- Unlock new games and features.  

> ⚠️ *This project is private and shared only for CS50 evaluation purposes.*  


---



## **Preview**

Here’s a quick preview of how the Flash Portal works! Watch the navigation through the web app below.

![imac](https://github.com/user-attachments/assets/7c27321c-b09c-4548-8bd5-aad052d46b1c)
![iphone15](https://github.com/user-attachments/assets/72c695cc-35d2-4521-acd1-d077342da7cc)



*(this gif is a quick preview of navigating the web app.)*

## **🎥 Video Demo**  
📹 [Watch the demo on YouTube!](#) *(Replace this link with your demo.)*


---



## **💻 Technologies Used**
| **Category**      | **Technologies**                           |
|-------------------|--------------------------------------------|
| **Languages**      | ![HTML](https://img.shields.io/badge/-HTML-orange) ![CSS](https://img.shields.io/badge/-CSS-blue) ![JavaScript](https://img.shields.io/badge/-JavaScript-yellow) ![Python](https://img.shields.io/badge/-Python-green) |
| **Frameworks**     | ![Flask](https://img.shields.io/badge/-Flask-black) ![Bootstrap](https://img.shields.io/badge/-Bootstrap-purple) |
| **Database**       | ![SQLite](https://img.shields.io/badge/-SQLite-lightblue) |
| **Other Tools**    | Jinja2, Flask-WTF                        |


---



## **🚀 Features**  

✨ **Game Collection**: Access a curated selection of Flash games.  
✨ **Progress Tracking**: Earn points and track achievements.  
✨ **Unlockable Content**: Use points to unlock additional games.  
✨ **Responsive Design**: Fully optimized for all devices.  
✨ **Secure Authentication**: Safe and reliable login system.  


---



## 📖 **Step-by-Step: How to Run the Web App**

1. **Clone the repository:**
    ```bash
    git clone git@github.com:Ztew-Rot/CS50-Final-project.git "folder-name"
    ```

2. **Navigate to project directory:**
    ```bash
    cd folder-name
    ```

3. **Activate the virtual environment:**
    ```bash
    source venv/bin/activate    # On Unix/MacOS
    # OR
    .\venv\Scripts\activate     # On Windows
    ```
    All required dependencies are already installed in the virtual environment.

4. **Run the Flask server:**
    ```bash
    flask run
    ```

5. **Access the web app:**
    Open your browser and go to http://127.0.0.1:5000

---

## **📂 File Structure** 
```bash
/flash_session    # Stores Flask session data for user authentication and state management
/static
    /games       # Game assets and Flash files (.swf)
    /js          # Ruffle framework implementation and custom JavaScript
        ruffle.js      # Ruffle Flash emulator
        game-loader.js # Custom game loading logic
    /css
        style.css     # Main stylesheet for website theming
    /images      # Website images and assets
/templates
    layout.html      # Base template with common elements (header, footer)
    auth.layout.html # Authentication-specific template (login, register)
    index.html      # Homepage template
    games.html      # Games library view
    profile.html    # User profile page
    ...
/venv            # Python virtual environment (contains project dependencies)
app.py           # Main Flask application (routes, configuration)
helpers.py       # Utility functions and helper methods
database.db      # SQLite database for user data and game progress
deploy.yml       # Environment variables and deployment configuration
requirements.txt # List of Python package dependencies
README.md        # Project documentation
    
```

---

## 📈 **Future Improvements**

<li>  
Add More Games: Expanding the game library.
</li>

<li>
Implement Leaderboards: Gamify the experience with global rankings.
</li>    
    
<li>
Multiplayer Mode: Allow users to compete in real-time.
</li>    

<li>
Enhanced Visuals: Improve UI/UX for a more immersive experience.
</li>    

---

## **📜 Disclaimer**
 
 ⚠️ **Private Project**:
 
This project is not open-source and shared exclusively for CS50 evaluation. Plans for public hosting include robust security measures to protect backend functionality and data integrity.
