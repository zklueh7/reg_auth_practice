from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_practice"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

@app.route("/")
def home():
    """Homepage, redirects to register page"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def registration_form():
    """Show and submit new user register form"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        newUser = User.register(username=username, password=password,email=email,
                       first_name=first_name, last_name=last_name)
        db.session.add(newUser)
        db.session.commit()
        return redirect("/secret")
    else:
        return render_template("register_form.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login_form():
    """Show and submit user login form"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username=username, password=password)
        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]
    return render_template("login_form.html", form=form)

@app.route("/secret")
def secret():
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        return render_template("secret.html")
    
@app.route("/logout")
def logout():
    """Log out a user"""
    session.pop("username")
    return redirect("/")

@app.route("/users/<username>")
def user_detail(username):
    """Show info about a given user upon login"""
    user = User.query.get(username)
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        return render_template("user_detail.html", user=user)
