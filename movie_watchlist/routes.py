from flask import Blueprint, render_template, session, redirect, request, current_app, url_for
from movie_watchlist.forms import MovieForm
import uuid
from movie_watchlist.models import Movie
from dataclasses import asdict

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

@pages.route("/")
def index():
    movies_data = current_app.db.movies.find({})
    movies = [Movie(**movie) for movie in movies_data]
    
    return render_template("index.html", title = "Movie Watchlist", movies=movies)

@pages.route("/add", methods=["GET", "POST"])
def add_movie():
    form = MovieForm()
    
    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data
        )
        
        current_app.db.movies.insert_one(asdict(movie))
        
        return redirect(url_for(".index"))
    
    return render_template("new_movie.html", title="Movie Watchlist - Add Movie", form=form)






@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
        
    return redirect(request.args.get("current_page"))