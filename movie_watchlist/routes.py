from flask import Blueprint, render_template, session, redirect, request, current_app, url_for, flash
from movie_watchlist.forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
import uuid
from movie_watchlist.models import Movie, User
from dataclasses import asdict
import datetime
from passlib.hash import pbkdf2_sha256
import functools

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")



def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper

@pages.route("/")
@login_required
def index():
    users = current_app.db["users"]
    movies = current_app.db["movies"]
    
    user_data = users.find_one({"email": session["email"]})
    if user_data is None:
        return redirect(url_for(".login"))
    else:
        user = User(**user_data)
    
    movies_data = movies.find({"_id": {"$in" : user.movies}})
    movies = [Movie(**movie) for movie in movies_data]
    
    return render_template("index.html", title = "Movie Watchlist | Home", movies=movies)

@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        
        users = current_app.db["users"]
        users.insert_one(asdict(user))
        
        flash("User registered successfully!", "success")
        
        return redirect(url_for(".login"))
        
    return render_template("register.html", title="Move Watchlist | Register", form=form)

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        print(session.get("email"))
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        users = current_app.db["users"]
        user_data = users.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="Movies Watchlist | Login", form=form)

@pages.route("/logout")
@login_required
def logout():
    current_theme = session.get("theme")
    session.clear()
    session["theme"] = current_theme
    
    return redirect(url_for(".login"))

@pages.route("/add", methods=["GET", "POST"])
@login_required
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
        current_app.db.users.update_one({"_id": session["user_id"]}, {"$push": {"movies": movie._id}})
        
        return redirect(url_for(".index"))
    
    return render_template("new_movie.html", title="Movie Watchlist | Add Movie", form=form)

@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_movie(_id):
    movie = Movie(**current_app.db.movies.find_one({"_id": _id}))
    form = ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title = form.title.data
        movie.director = form.director.data
        movie.year = form.year.data
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data
        
        current_app.db.movies.update_one({"_id": movie._id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=movie._id))
    return render_template("movie_form.html", movie=movie, form=form)

@pages.route("/movie/<string:_id>")
@login_required
def movie(_id: str):
    movie_data = current_app.db.movies.find_one({"_id": _id})
    movie = Movie(**movie_data)
    return render_template("movie_details.html", movie=movie)

@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movies.update_one({"_id": _id}, {"$set": {"rating": rating}})
    
    return redirect(url_for(".movie", _id=_id))

@pages.get("/movie/<string:_id>/watch")
@login_required
def watch_today(_id):
    current_app.db.movies.update_one({"_id": _id}, {"$set": {"last_watched": datetime.datetime.today()}})
    
    return redirect(url_for('.movie', _id=_id))

@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
        
    return redirect(request.args.get("current_page"))