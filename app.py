from flask import Flask, redirect, url_for, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "HELLOO!!"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    phone_no = db.Column("phone_no", db.Integer)
    email = db.Column("email", db.String(30), unique=True)
    username = db.Column("username", db.String(100), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)

    def __init__(self, name, email, phone_no, username, password):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.username = username
        self.password = password

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone_no = request.form["phone_no"]
        username = request.form["username"]
        password = request.form["password"]

        #checking if there is already existing email
        found_user = users.query.filter_by(email=email).first()
        if found_user:
            return render_template("signup.html", error="Email already present")
        
        #adding the user to the database
        usr = users(name, email, phone_no, username, password)
        db.session.add(usr)
        db.session.commit()

        return redirect(url_for("login"))
    else:
        return render_template("signup.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        found_user = users.query.filter_by(username=username).first()
        if found_user and found_user.password == password:
            session["user"] = found_user._id
            return redirect(url_for("user"))
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        found_user = users.query.get(session["user"])
        email = found_user.email
        return render_template("user.html", email = email)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    user = session["user"]
    session.pop("user")
    return render_template("logout.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)