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
    status = db.Column("status", db.String(20), default="active")                   #active, blacklisted

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
    status = db.Column("status", db.String(20), default="pending")          #pending, active, rejected, blacklisted, assigned

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
    status = db.Column("status", db.String(100), default="open")                #active, closed, completed
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
@app.route("/signup", methods=["POST", "GET"])          #Signup page
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone_no = request.form["phone_no"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        #Backend validation for signup page
        if len(phone_no) != 10:
            return render_template("signup.html", error="Enter a valid phone number")
        if '@' not in email or '.' not in email:
            return render_template("signup.html", error="Enter a valid Email ID")
        if not username.isalnum():
            return render_template("signup.html", error="Enter a valid username")
        if len(password) <= 4:
            return render_template("signup.html", error="Password must contain 5 or more characters")

        
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
def login():                                        #Login page
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        #Backend validation for login page
        if not username.isalnum():
            return render_template("signup.html", error="Enter a valid username")
        if len(password) <= 4:
            return render_template("signup.html", error="Password must contain 5 or more characters")

        table = {"admin": admin, "staff": staffs, "user": users}[role]

        found_user = table.query.filter_by(username=username).first()
        if found_user and found_user.password == password:
            if role == "staff":
                if found_user.status == "pending":
                    return render_template("login.html", error="The account approval is still pending!")
                elif found_user.status == "active" or found_user.status == "assigned":
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
    
@app.route("/logout")
def logout():                                           #Logout Page
    session.clear()
    return render_template("logout.html")

#ADMIN
@app.route("/admin")
def admin_dashboard():                                  #Admin Dashboard
    if "admin" in session:
        all_treks = treks.query.all()
        total_active_treks = treks.query.filter_by(status="active").count()
        total_treks = treks.query.count()

        active_staff = staffs.query.filter(staffs.status.in_(["active", "assigned"])).all()
        total_staff = staffs.query.count()

        total_users = users.query.count()

        all_bookings = bookings.query.all()
        total_bookings = bookings.query.count()

        pending_req = staffs.query.filter_by(status="pending").all()
        return render_template(
            "admin.html", 
            pending_req=pending_req, 
            active_staff=active_staff, 
            all_bookings=all_bookings, 
            all_treks = all_treks, 
            total_staff=total_staff,
            total_active_treks=total_active_treks, 
            total_treks=total_treks, 
            total_bookings=total_bookings,
            total_users=total_users
        )
    
    else:
        return redirect(url_for("login"))
    
@app.route("/admin/trek-management", methods=["POST", "GET"])
def admin_trek_management():                                        #Admin Trek Management
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
    
@app.route("/admin/search", methods=["POST"])
def admin_search():
    if "admin" not in session:
        return redirect(url_for("login"))

    search_id = request.form["id"]
    search_type = request.form["val"]

    model = {"trek": treks, "staff": staffs, "user": users}.get(search_type)

    search_result = None
    if model:
        search_result = db.session.get(model, search_id)

    #Getting everything the dashboard normally needs again
    all_treks = treks.query.all()
    total_active_treks = treks.query.filter_by(status="active").count()
    total_treks = treks.query.count()
    active_staff = staffs.query.filter(staffs.status.in_(["active", "assigned"])).all()
    total_staff = staffs.query.count()
    total_users = users.query.count()
    all_bookings = bookings.query.all()
    total_bookings = bookings.query.count()
    pending_req = staffs.query.filter_by(status="pending").all()

    return render_template(
        "admin.html",
        pending_req=pending_req,
        active_staff=active_staff,
        all_bookings=all_bookings,
        all_treks=all_treks,
        total_staff=total_staff,
        total_active_treks=total_active_treks,
        total_treks=total_treks,
        total_bookings=total_bookings,
        total_users=total_users,
        search_result=search_result,
        search_type=search_type
    )

@app.route("/admin/reassign-staff/<int:trek_id>", methods=["POST"])
def reassign_staff(trek_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    found_trek = db.session.get(treks, trek_id)
    new_staff_id = int(request.form["assigned_staff_id"])

    if found_trek:
        if found_trek.assigned_staff_id:
            old_staff = db.session.get(staffs, found_trek.assigned_staff_id)
            if old_staff:
                old_staff.status = "active"

        found_trek.assigned_staff_id = new_staff_id
        new_staff = db.session.get(staffs, new_staff_id)
        if new_staff:
            new_staff.status = "assigned"

        db.session.commit()

    return redirect(url_for("admin_trek_management"))

@app.route("/admin/staff-blacklist/<int:staff_id>", methods=["POST"])
def staff_blacklist(staff_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    found_staff = db.session.get(staffs, staff_id)
    if found_staff:
        # Free up any trek this staff member was assigned to
        assigned_trek = treks.query.filter_by(assigned_staff_id=staff_id).first()
        if assigned_trek:
            assigned_trek.assigned_staff_id = None

        found_staff.status = "blacklisted"
        db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/user-blacklist/<int:user_id>", methods=["POST"])
def user_blacklist(user_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    found_user = db.session.get(users, user_id)
    if found_user:
        active_bookings = bookings.query.filter_by(user_id=user_id, status="booked").all()
        for b in active_bookings:
            found_trek = db.session.get(treks, b.trek_id)
            if found_trek:
                found_trek.available_slots += 1
                found_trek.status = "active"
            b.status = "cancelled"

        found_user.status = "blacklisted"
        db.session.commit()

    return redirect(url_for("admin_dashboard"))

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

@app.route("/user")
def user_dashboard():
    if "user" in session:
        all_treks = treks.query.all()
        user_bookings = bookings.query.filter_by(user_id=session["user"], status="booked").all()
        booked_trek_ids = [i.trek_id for i in user_bookings]

        return render_template("user.html", all_treks=all_treks, booked_trek_ids=booked_trek_ids)
    else:
        return redirect(url_for("login"))
    
@app.route("/user/search", methods=["POST"])
def user_search():
    if "user" not in session:
        return redirect(url_for("login"))

    search_id = request.form["id"]
    search_result = db.session.get(treks, search_id)

    # Re-fetch everything the dashboard normally needs
    all_treks = treks.query.all()
    user_id = session["user"]
    all_user_bookings = bookings.query.filter_by(user_id=user_id).order_by(bookings.booking_date.desc()).all()
    active_bookings = [b for b in all_user_bookings if b.status == "booked"]
    booked_trek_ids = [b.trek_id for b in active_bookings]

    return render_template(
        "user.html",
        all_treks=all_treks,
        booked_trek_ids=booked_trek_ids,
        active_bookings=active_bookings,
        all_user_bookings=all_user_bookings,
        search_result=search_result
    )
    
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
    if "staff" not in session:
        return redirect(url_for("login"))

    found_staff = db.session.get(staffs, session["staff"])
    assigned_treks = treks.query.filter_by(assigned_staff_id=found_staff._id).all()

    trek_bookings = {}
    for trek in assigned_treks:
        trek_bookings[trek._id] = bookings.query.filter_by(trek_id=trek._id, status="booked").all()

    return render_template(
        "staff.html",
        email=found_staff.email,
        assigned_treks=assigned_treks,
        trek_bookings=trek_bookings
    )

@app.route("/staff/trek-open/<int:trek_id>", methods=["POST"])
def staff_trek_open(trek_id):
    if "staff" not in session:
        return redirect(url_for("login"))

    found_trek = db.session.get(treks, trek_id)
    if found_trek and found_trek.assigned_staff_id == session["staff"]:
        found_trek.status = "active"
        db.session.commit()

    return redirect(url_for("staff_dashboard"))

@app.route("/staff/trek-close/<int:trek_id>", methods=["POST"])
def staff_trek_close(trek_id):
    if "staff" not in session:
        return redirect(url_for("login"))

    found_trek = db.session.get(treks, trek_id)
    if found_trek and found_trek.assigned_staff_id == session["staff"]:
        found_trek.status = "closed"
        db.session.commit()

    return redirect(url_for("staff_dashboard"))

@app.route("/staff/remove-participant/<int:booking_id>", methods=["POST"])          #Same code as user blacklisting just changed to staff context
def staff_remove_participant(booking_id):
    if "staff" not in session:
        return redirect(url_for("login"))

    found_booking = db.session.get(bookings, booking_id)
    if found_booking:
        found_trek = db.session.get(treks, found_booking.trek_id)
        if found_trek and found_trek.assigned_staff_id == session["staff"]:
            found_booking.status = "cancelled"
            found_trek.available_slots += 1
            found_trek.status = "active"
            db.session.commit()

    return redirect(url_for("staff_dashboard"))

@app.route("/staff/update-slots/<int:trek_id>", methods=["POST"])
def staff_update_slots(trek_id):
    if "staff" not in session:
        return redirect(url_for("login"))
    
    found_trek = db.session.get(treks, trek_id)
    
    if found_trek.assigned_staff_id != session["staff"]:
        flash("You are not assigned to this trek")
        return redirect(url_for("staff_dashboard"))
    
    new_slots = int(request.form["slots"])
    
    if new_slots > found_trek.total_slots:
        flash("Slots cannot exceed total slots")
        return redirect(url_for("staff_dashboard"))
    
    found_trek.available_slots = new_slots
    db.session.commit()
    flash("Slots updated successfully")
    return redirect(url_for("staff_dashboard"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not admin.query.first():
            default_admin = admin("admin", "admin123")
            db.session.add(default_admin)
            db.session.commit()

    app.run(debug=True)
