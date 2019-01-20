import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def overlap(start1, end1, start2, end2):
    overlap = dict()
    # Calculate break overlap duration (in days)
    try:
        overlap['startdate'] = max(todate(start1), todate(start2))
        overlap['enddate'] = min(todate(end1), todate(end2))
    except TypeError:
        overlap['startdate'] = max(start1, start2)
        overlap['enddate'] = min(end1, end2)
    overlap['duration'] = (overlap['enddate'] - overlap['startdate']).days + 1
    # Replace datetime objects with just dates
    try:
        overlap['startdate'] = overlap['startdate'].date()
        overlap['enddate'] = overlap['enddate'].date()
    except AttributeError:
        pass
    # If the duration is < 0, there is no overlap between the two date ranges
    if overlap['duration'] < 1:
        return None
    return overlap


# Convert mysql date string into datetime object
def todate(date):
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return datetime.datetime.strptime(date, '%b %d, %Y')


# Convert mysql datetime string into datetime object
def todatetime(dt):
    return datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M')


# Convert to datetime.date object if input is a string
def formatdate(date):
    if type(date) is str:
        date = todate(date)
    return date.strftime('%b %d, %Y')

# Format a datetime into the string type to be displayed on the website
def formatdatetime(dt):
    if type(dt) is str:
        dt = todatetime(date)
    return dt.strftime('%I:%M%p %b %d, %Y')

