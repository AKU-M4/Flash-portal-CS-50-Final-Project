from flask import session, request, render_template, Flask, url_for
from flask_session import Session
from livereload import Server

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

if (__name__)=="__main__":
    app.run(debug=True)

    # Use livereload to auto-reload on code changes
    server = Server(app.wsgi_app)
    server.watch('static/')       # Watches the 'static' folder
    server.watch('templates/')    # Watches the 'templates' folder
    server.serve(port=5000, debug=True)