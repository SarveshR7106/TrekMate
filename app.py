from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.secret_key = "HELLOO!!"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        user = request.form["email"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        email = session["user"]
        return render_template("user.html", email = email)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user")
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)