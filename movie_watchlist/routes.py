from flask import Blueprint, render_template, session, redirect, request
from movie_watchlist.forms import MovieForm


pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

@pages.route("/")
def index():
    return render_template("index.html", title = "Movie Watchlist")

@pages.route("/add", methods=["GET", "POST"])
def add_movie():
    form = MovieForm()
    
    if request.method == "POST":
        pass
    
    return render_template("new_movie.html", title="Movie Watchlist - Add Movie")






@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
        
    return redirect(request.args.get("current_page"))