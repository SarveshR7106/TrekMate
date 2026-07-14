#IMPORT STATEMENTS
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#CONFIG DETAILS
app = Flask(__name__)
app.secret_key = "HELLOO!!"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#DATABASES
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    phone_no = db.Column("phone_no", db.Integer)
    email = db.Column("email", db.String(30), unique=True)
    username = db.Column("username", db.String(100), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)
    status = db.Column("status", db.String(20), default="active")

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

class staffs(db.Model):   
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    phone_no = db.Column("phone_no", db.Integer)
    email = db.Column("email", db.String(30), unique=True)
    username = db.Column("username", db.String(100), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)
    status = db.Column("status", db.String(20), default="pending") #pending, active, rejected, blacklisted, assigned

    def __init__(self, name, email, phone_no, username, password):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.username = username
        self.password = password

    assigned_treks = db.relationship("treks", backref='staff_member')

class treks(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100), nullable = False)
    location = db.Column("location", db.String(100), nullable = False)
    difficulty = db.Column("difficulty", db.String(100))
    status = db.Column("status", db.String(100)) #open, closed, completed
    start_date = db.Column("start_date", db.Date)
    end_date = db.Column("end_date", db.Date)
    duration = db.Column("duration", db.Integer)
    total_slots = db.Column("total_slots", db.Integer)
    available_slots = db.Column("available_slots", db.Integer)
    assigned_staff_id = db.Column("assigned_staff_id", db.Integer, db.ForeignKey('staffs.id'))

    def __init__(self, name, location, difficulty, status, start_date, end_date, duration, total_slots, available_slots, assigned_staff_id=None):
        self.name = name
        self.location = location
        self.difficulty = difficulty
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.total_slots = total_slots
        self.available_slots = available_slots
        self.assigned_staff_id = assigned_staff_id

class bookings(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    booking_date = db.Column("booking_date", default=datetime.now)
    status = db.Column("status", db.String)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'))
    trek_id = db.Column("trek_id", db.Integer, db.ForeignKey('treks.id'))

    def __int__(self, booking_date, status, user_id=None, trek_id=None):
        self.booking_date = booking_date
        self.status = status
        self.user_id = user_id
        self.trek_id = trek_id

    booked_user = db.relationship('users', backref='bookings')
    booked_trek = db.relationship('treks', backref='bookings')

@app.route("/")
def home():
    return render_template("home.html")

#LOGIN AUTHENTICATION AND ACCOUNT REGISTRATION
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone_no = request.form["phone_no"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        #Backend validation for phone number
        if len(phone_no) != 10:
            return render_template("signup.html", error="Enter a valid phone number")

        role_val = {"user": users, "staff": staffs}[role]

        #checking if there is already existing email
        found_user = role_val.query.filter_by(email=email).first()
        if found_user:
            return render_template("signup.html", error="Email already present")
        
        found_username = role_val.query.filter_by(username=username).first()
        if found_username:
            return render_template("signup.html", error="Username already taken")
        
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

        table = {"admin": admin, "staff": staffs, "user": users}[role]

        found_user = table.query.filter_by(username=username).first()
        if found_user and found_user.password == password:
            if role == "staff":
                if found_user.status == "pending":
                    return render_template("login.html", error="The account approval is still pending!")
                elif found_user.status == "accepted":
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
        pending_req = staffs.query.filter_by(status="pending").all()
        active_staff = staffs.query.filter_by(status="active").all()
        return render_template("admin.html", pending_req=pending_req, active_staff=active_staff)
    
    else:
        return redirect(url_for("login"))
    
@app.route("/admin/trek-management", methods=["POST", "GET"])
def admin_trek_management():
    if "admin" in session:
        if request.method == "POST":
            name = request.form["name"]
            location = request.form["location"]
            difficulty = request.form["difficulty"]
            status = request.form["status"]
            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date() #We get date in this format only from browser and we cant change that
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date() #So to display it in different format we have to change in jinja2 and html
            duration = (end_date - start_date).days
            total_slots = int(request.form["total_slots"])
            available_slots = total_slots
            assigned_staff_id = request.form["assigned_staff_id"]

            trek_val = treks(name, location, difficulty, status, start_date, end_date, duration, total_slots, available_slots, assigned_staff_id)
            db.session.add(trek_val)
            assigned_staff = db.session.get(staffs, assigned_staff_id)
            assigned_staff.status = "assigned"
            db.session.commit()
            return redirect(url_for("admin_dashboard"))

        
        available_staff = staffs.query.filter_by(status="active").all()
        all_treks = treks.query.all()
        return render_template("admin_trek_management.html", available_staff=available_staff, all_treks = all_treks)
    else:
        return redirect(url_for("login"))

@app.route("/user")
def user_dashboard():
    if "user" in session:
        all_treks = treks.query.all()
        user_bookings = bookings.query.filter_by(user_id=session["user"]).all()
        booked_trek_ids = [i.trek_id for i in user_bookings]

        return render_template("user.html", all_treks=all_treks, booked_trek_ids=booked_trek_ids)
    else:
        return redirect(url_for("login"))
    
@app.route("/user/trek_booking/<int:trek_id>", methods=["POST"])
def trek_booking(trek_id):
    if "user" not in session:
        return redirect(url_for('login'))
    
    user_id = session["user"]
    found_trek = db.session.get(treks, trek_id)

    if found_trek:

        #To avoid overbooking
        if found_trek.available_slots <= 0:
            flash("There are no more slots")
            return redirect(url_for("user_dashboard"))
        
        new_booking = bookings(status="booked", user_id=user_id, trek_id=trek_id)
        found_trek.available_slots -= 1
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for("user_dashboard"))
    else:
        return redirect(url_for("user_dashboard"))
    
@app.route("/user/trek_cancelling/<int:trek_id>", methods=["POST"])
def trek_cancelling(trek_id):
    if "user" not in session:
        return redirect(url_for('login'))
    
    user_id = session["user"]
    found_trek = db.session.get(treks, trek_id)
    found_booking = bookings.query.filter_by(trek_id=trek_id, user_id=user_id, status="booked").first()
    if found_trek:
        found_booking.status = "cancelled"
        found_trek.available_slots += 1
        found_trek.status = "active"
        db.session.commit()
        return redirect(url_for("user_dashboard"))
    else:
        return redirect(url_for("user_dashboard"))
    
@app.route("/staff")
def staff_dashboard():
    if "staff" in session:
        found_staff = staffs.query.get(session["staff"])
        email = found_staff.email
        return render_template("staff.html", email=email)
    else:
        return redirect(url_for("login"))

@app.route("/admin/staff-approval/<int:staff_id>", methods=['POST']) #This <int:staff_id> is for flask to know which staff (based on id) was accepted/rejected
def staff_approval(staff_id): #Flask directly passes the attribute and for a split second only it stays in that URL and redirects back to admin
    if "admin" not in session:
        return redirect(url_for("login"))
    
    found_staff = db.session.get(staffs, staff_id)
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