# **🎮 Flash Portal**  

*Your gateway to nostalgic gaming.* 

![flash portal banner1](https://github.com/user-attachments/assets/ab4fa7ee-c8d8-4824-bbda-2cbbb19e9be3)



---



## **🌟 About the Project**  

Flash Portal is a full-stack web application designed to revive and preserve the joy of classic Flash games, ensuring these nostalgic treasures remain accessible in the modern era.

With the decline of Adobe Flash and its compatibility issues, Flash Portal aims to bring back the experience of playing iconic Flash games through modern technologies. Users can:

- Access a curated library of classic Flash games, playable directly on the platform.
- Track progress and achievements, making the experience more rewarding.
- Unlock new games using points earned by playing and completing challenges.

> ⚠️ *This project is private and shared only for CS50 evaluation purposes.*  


---



## **Preview**

Here’s a quick preview of how the Flash Portal works! Watch the navigation through the web app below.

![imac](https://github.com/user-attachments/assets/7c27321c-b09c-4548-8bd5-aad052d46b1c)
![iphone15](https://github.com/user-attachments/assets/72c695cc-35d2-4521-acd1-d077342da7cc)



*(this gif is a quick preview of navigating the web app.)*

## **🎥 Video Demo**  
📹 [Watch the demo on YouTube!](#) *(https://youtu.be/TlkFrrDgGGI)*


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

## **⚖️ Design Choices**

- **Game Accessibility**

    The decision to use the Ruffle Flash emulator ensures the longevity of Flash games while making them compatible with modern browsers.

- **Database Selection**
  
    SQLite was chosen for its simplicity and lightweight nature, making it suitable for this project’s scope.

- **Frontend and Backend**
  
    Using Flask as the backend framework provided flexibility, while Bootstrap ensured a responsive and user-friendly interface.

- **User Experience**
  
    A focus was placed on intuitive navigation, with clear progress tracking and unlockable content to keep users engaged.

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

## 📈 **Future Improvements**

<li>  
Add More Games: Expanding the game library.
</li>

<li>
Implement Leaderboards: Gamify the experience with global rankings.
</li> 

<li>
Daily Challenge System: Complete challenges to earn coins and unlock new games.
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
