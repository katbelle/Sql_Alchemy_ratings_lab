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


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


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
