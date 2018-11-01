"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


# Flask way to print in debug: app.logger.info('')


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/movies")
def show_movies():
	"""Show list of movies"""

	movies = Movie.query.distinct(Movie.title).order_by(Movie.title).all()
	return render_template("movie_list.html", movies=movies)


@app.route("/users/<int:user_id>")
def show_user_info(user_id):
	"""Show user information page."""

	age = User.query.get(user_id).age
	zipcode = User.query.get(user_id).zipcode

	movie_scores = Rating.query.filter_by(user_id=user_id).options(db.joinedload('movie')).all()
	user_movies = []

	for movie_score in movie_scores:
		user_movies.append((movie_score.movie.title, movie_score.score))

	return render_template("user_info.html", user_id=user_id,
											 age=age,
										     zipcode=zipcode,
										     user_movies=user_movies)

@app.route("/movies/<int:movie_id>")
def show_movie_details(movie_id):

	scores = Rating.query.filter_by(movie_id=movie_id).options(db.joinedload('movie')).all()
	movie_scores = []
	movie = Movie.query.get(movie_id)

	for score in scores:
		movie_scores.append((score.user_id, score.score))

	return render_template("movie_details.html", movie_scores=movie_scores,
											     movie=movie)


@app.route("/movie_details", methods=["POST"])
def process_rating():
	new_score = int(request.form.get("input_rating"))
	movie_id = int(request.form.get("movie_id"))

	if session["logged_in_user"]:
		user_id = session["logged_in_user"]

		if Rating.query.filter(Rating.user_id==user_id, Rating.movie_id==movie_id).first():
			user = Rating.query.filter(Rating.user_id==user_id, Rating.movie_id==movie_id).first()
			user.score = new_score

			flash("Your rating has been updated!")

		else:
			user = Rating(movie_id=movie_id, user_id=user_id, score=new_score)
			flash("Kat ded!")

		db.session.add(user) # does this update or add new row?
		db.session.commit()

		return redirect(f"/movies/{movie_id}")


@app.route("/registration_form", methods=["GET", "POST"])
def register_process():
	"""Registration form and process"""

	if request.method == "GET":
		return render_template("registration_form.html")

	else:
		email = request.form.get("email")
		password = request.form.get("password")

		if not User.query.filter(User.email == email).first():
			user = User(email=email, password=password)
			db.session.add(user)
			db.session.commit()
			return redirect("/")
		else:
			flash('That e-mail already exists!')
			return render_template("registration_form.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	"""Log in."""

	if request.method == "GET":
		return render_template("login.html")

	else:
		email = request.form.get("email")
		password = request.form.get("password")	

		q = User.query

		if q.filter((User.email == email), (User.password == password)).first():
			session["logged_in_user"] = q.filter(User.email == email).one().user_id

			flash("Logged in!")
			return redirect("/")
		else:
			flash("The e-mail or password is incorrect.")
			return render_template("login.html")


@app.route("/logout")
def logout():
	"""Log out."""

	del session["logged_in_user"]
	flash("Successfully logged out!")
	return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
