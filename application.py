import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import requests
import json

from helpers import apology, login_required, overlap, todate, todatetime, formatdate, formatdatetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("postgres://ueqricbvdfbult:c611a389dd0dd552b91f2ee9f625e6cb0fa7047e80f26178c824896327568c01@ec2-54-225-150-216.compute-1.amazonaws.com:5432/d7gqtugbhnn48d")


@app.route("/")
@login_required
def index():
    # Generate data to be passed to render_template
    data = dict()
    link = dict()
    link['id'] = db.execute('SELECT link FROM users WHERE id=:id', id=session["user_id"])[0]['link']
    if not link['id']:
        # User is not linked yet
        # Get requests from db
        requests = db.execute('SELECT fromid, datetime FROM requests WHERE toid=:id', id=session["user_id"])
        for request in requests:
            fromid = request['fromid']
            fromname = db.execute('SELECT username FROM users WHERE id=:id', id=fromid)[0]['username']
            request['fromname'] = fromname
        data['requests'] = requests
        return render_template("index.html", data=data)
    else:
        # User is already linked
        link['name'] = db.execute('SELECT username FROM users WHERE id=:id', id=link['id'])[0]['username']
        breaks = db.execute('SELECT startdate, enddate FROM break WHERE id=:id', id=session["user_id"])
        linkbreaks = db.execute('SELECT startdate, enddate FROM break WHERE id=:id', id=link['id'])
        overlaps = []
        # Calculate overlaps
        for br in breaks[:]:
            for lbr in linkbreaks[:]:
                o = overlap(br['startdate'], br['enddate'], lbr['startdate'], lbr['enddate'])
                if o:
                    br['startdate'] = formatdate(br['startdate'])
                    br['enddate'] = formatdate(br['enddate'])
                    lbr['startdate'] = formatdate(lbr['startdate'])
                    lbr['enddate'] = formatdate(lbr['enddate'])
                    o['startdate'] = formatdate(o['startdate'])
                    o['enddate'] = formatdate(o['enddate'])
                    overlaps.append({'me': br, 'link': lbr, 'overlap': o})
                    breaks.remove(br)
                    linkbreaks.remove(lbr)
                    break
        # Take remaining unpaired breaks and append them to the end of overlaps
        while len(breaks) > 0:
            br = breaks.pop(0)
            br['startdate'] = formatdate(br['startdate'])
            br['enddate'] = formatdate(br['enddate'])
            overlaps.append({'me': br, 'link': None, 'overlap': None})
        while len(linkbreaks) > 0:
            lbr = linkbreaks.pop(0)
            lbr['startdate'] = formatdate(lbr['startdate'])
            lbr['enddate'] = formatdate(lbr['enddate'])
            overlaps.append({'me': None, 'link': lbr, 'overlap': None})
        # Sort break pairs by starting date
        overlaps.sort(key=lambda x: todate(x['me']['startdate']) if x['me'] else todate(x['link']['startdate']))
        data['breaks'] = overlaps
        data['link'] = link
        # Get trips from db
        trips = db.execute('SELECT * FROM trips WHERE id=:id OR id=:link', id=session["user_id"], link=link['id'])

        for trip in trips[:]:
            if todatetime(trip['enddate']) < datetime.datetime.now():
                # Remove trips that have already ended
                db.execute('DELETE FROM trips WHERE enddate=:end AND id=:id', end=trip['enddate'], id=trip['id'])
                trips.remove(trip)
            elif todatetime(trip['startdate']) < datetime.datetime.now() < todatetime(trip['enddate']):
                # Trip is ongoing
                trip['ongoing'] = True
                trip['time'] = todatetime(trip['enddate']) - datetime.datetime.now()
            else:
                # Trip has yet to start
                trip['ongoing'] = False
                trip['time'] = todatetime(trip['startdate']) - datetime.datetime.now()
            # Convert MySQL datetime strings into python datetimes objects
            trip['startdate'] = todatetime(trip['startdate'])
            trip['enddate'] = todatetime(trip['enddate'])
        if len(trips) > 0:
            trips.sort(key=lambda x: x['startdate'])
            for trip in trips:
                # Convert datetime objects into more readable strings
                trip['startstr'] = formatdatetime(trip['startdate'])
                trip['endstr'] = formatdatetime(trip['enddate'])
                # Add usernames to trip dict
                if trip['id'] == session['user_id']:
                    trip['name'] = 'Me'
                else:
                    trip['name'] = link['name']
        data['trips'] = trips
        return render_template("linked.html", data=data)


@app.route("/linkrequest", methods=["POST"])
@login_required
def linkrequest():
    if session['link']:
        return apology("Already linked with someone! >:(")
    linkname = request.form.get('linkreq')
    if not linkname:
        return apology("Enter username to be linked with.")
    linkid = db.execute('SELECT id, link FROM users WHERE username=:username', username=linkname)
    if len(linkid) == 0:
        return apology("User not found.")
    if linkid[0]['link']:
        return apology("User '" + linkname + "' is already linked with someone!")
    linkid = linkid[0]['id']
    if linkid == session['user_id']:
        return apology("Cannot link with yourself!")
    # Send a link request to a user by storing it into 'requests' table
    db.execute("INSERT INTO requests (toid, fromid) VALUES(:to, :fromid)", to=linkid, fromid=session['user_id'])
    return redirect("/")


@app.route("/accept", methods=["POST"])
@login_required
def accept():
    # Accept a link request from the given id
    link = request.form.get('acceptid')
    if not link:
        return apology('Something went wrong!')
    # Update links in users table
    db.execute('UPDATE users Set link = :link WHERE id=:id', id=session['user_id'], link=link)
    db.execute('UPDATE users Set link = :link WHERE id=:id', id=link, link=session['user_id'])
    # Clear all associated pending requests
    db.execute('DELETE FROM requests WHERE fromid=:id OR toid=:id', id=session['user_id'])
    db.execute('DELETE FROM requests WHERE fromid=:id OR toid=:id', id=link)
    return redirect("/")


@app.route("/timer", methods=["POST"])
@login_required
def timer():
    # Display a timer counting down towards given time
    if not request.form.get('time'):
        return apology('Something went wrong!')
    time = request.form.get('time').strip()
    time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return render_template("timer.html", time=time)


@app.route("/breaks", methods=["GET", "POST"])
@login_required
def breaks():
    if request.method == "POST":
        if not request.form.get('start1') or not request.form.get('end1'):
            return apology("Enter start and end date of break.")
        counter = 1
        # Clear original break schedule from db
        db.execute('DELETE FROM break WHERE id=:id', id=session['user_id'])
        # Insert new break schedule into db
        while (request.form.get('startdate' + str(counter)) and request.form.get('enddate' + str(counter))):
            start = request.form.get('startdate' + str(counter))
            end = request.form.get('enddate' + str(counter))
            db.execute("INSERT INTO break (id, startdate, enddate) VALUES(:id, :start, :end)", start=start, end=end, id=session["user_id"])
            print(start, end)
            counter += 1
        return redirect("/")
    else:
        # Get existing breaks and pass them to render_template to be edited by user
        breaks = db.execute('SELECT startdate, end FROM break WHERE id=:id', id=session["user_id"])
        breaks.sort(key=lambda x: todate(x['startdate']))
        return render_template("break.html", breaks=breaks)


@app.route("/trips", methods=["GET", "POST"])
@login_required
def trips():
    if request.method == "POST":
        if not request.form.get('startdate') or not request.form.get('enddate'):
            return apology("Enter start and end date of trip.")
        # Add inputted trip to db trips table
        start = request.form.get('startdate')
        end = request.form.get('enddate')
        db.execute("INSERT INTO trips (id, startdate, enddate) VALUES(:id, :start, :end)", start=start, end=end, id=session["user_id"])
        return redirect("/")
    else:
        return render_template("trips.html")


@app.route("/check", methods=["GET"])
def check():
    # Return true if username available, else false, in JSON format
    username = request.args.get("username")
    if len(username) >= 1:
        return jsonify(len(db.execute("SELECT * FROM users WHERE username = :username", username=username)) == 0)
    return jsonify("false")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["link"] = rows[0]["link"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # print('recieved registration request')
        username = request.form.get("username")
        if not username:
            return apology("Please enter a username.")
        password = request.form.get("password")
        if not password:
            return apology("Please enter a password.")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("Please enter your password again.")
        elif password != confirmation:
            return apology("Passwords do not match.")
        passwordHash = generate_password_hash(password)
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=username, hash=passwordHash)
        if not result:
            return apology("This username is already in use.")
        else:
            session["user_id"] = db.execute("SELECT id FROM users WHERE username=:username", username=username)[0]["id"]
            session["username"] = username
            session["link"] = None
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        cur_password = request.form.get("cur_password")
        if not cur_password:
            return apology("Must enter current password.")
        if not check_password_hash(db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])[0]["hash"], cur_password):
            return apology("Incorrect current password")
        password = request.form.get("password")
        if not password:
            return apology("Must enter a new password.")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("Must confirm new password.")
        if password != confirmation:
            return apology("Passwords do not match")
        if check_password_hash(db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])[0]["hash"], password):
            return apology("New password is the same as the current password")
        db.execute("UPDATE users SET hash=:hash WHERE id=:id", hash=generate_password_hash(password), id=session["user_id"])
        return redirect("/")
    else:
        return render_template("password.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
