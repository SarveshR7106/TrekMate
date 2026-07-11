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
    status = db.Column("status", db.String(20), default="pending")

    def __init__(self, name, email, phone_no, username, password):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.username = username
        self.password = password

class admin(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    username = db.Column("username", db.String(100), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class staff(db.Model):   
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    phone_no = db.Column("phone_no", db.Integer)
    email = db.Column("email", db.String(30), unique=True)
    username = db.Column("username", db.String(100), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)
    status = db.Column("status", db.String(20), default="pending")

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
        role = request.form["role"]

        role_val = {"user": users, "staff": staff}[role]

        #checking if there is already existing email
        found_user = role_val.query.filter_by(email=email).first()
        if found_user:
            return render_template("signup.html", error="Email already present")
        
        #adding the user to the database
        usr = role_val(name, email, phone_no, username, password)
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
        role = request.form["role"]

        table = {"admin": admin, "staff": staff, "user": users}[role]

        found_user = table.query.filter_by(username=username).first()
        if found_user and found_user.password == password:
            if role == "staff":
                if found_user.status == "pending":
                    return render_template("login.html", error="The account approval is still pending!")
                elif found_user.status == "active":
                    session[role] = found_user._id
                    return redirect(url_for(f"{role}_dashboard"))
                else:
                    return render_template("login.html", error="Your account request has been rejected. Contact the admin for further information")
            else:
                session[role] = found_user._id
                return redirect(url_for(f"{role}_dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")
    
@app.route("/admin")
def admin_dashboard():
    if "admin" in session:
        pending_req = staff.query.filter_by(status="pending").all()
        return render_template("admin.html", pending_req=pending_req)
    
    else:
        return redirect(url_for("login"))

@app.route("/user")
def user_dashboard():
    if "user" in session:
        found_user = users.query.get(session["user"])
        email = found_user.email
        return render_template("user.html", email = email)
    else:
        return redirect(url_for("login"))
    
@app.route("/staff")
def staff_dashboard():
    if "staff" in session:
        found_staff = staff.query.get(session["staff"])
        email = found_staff.email
        return render_template("staff.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/admin/staff-approval/<int:staff_id>", methods=['POST']) #This <int:staff_id> is for flask to know which staff (based on id) was accepted/rejected
def staff_approval(staff_id): #Flask directly passes the attribute and for a split second only it stays in that URL and redirects back to admin
    if "admin" not in session:
        return redirect(url_for("login"))
    
    found_staff = db.session.get(staff, staff_id)
    action = request.form["action"]
    print(action)

    if action == "accept":
        found_staff.status = "active"
    elif action == "reject":
        found_staff.status = "rejected"

    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/logout")
def logout():
    print(session)
    session.clear()
    print(session)
    return render_template("logout.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not admin.query.first():
            default_admin = admin("admin", "admin123")
            db.session.add(default_admin)
            db.session.commit()

    app.run(debug=True)