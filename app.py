import os
import requests
import urllib.parse
from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///listy.db")
def search(title):
    try:
        
        url = f"https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={urllib.parse.quote_plus(title)}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        data = response.json()
        return data["results"]
    except (KeyError, TypeError, ValueError):
        return None

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
        
        return redirect("/profile/" + str(session["user_id"]))
    
@app.route("/profile/<id>", methods=["POST", "GET"])
@login_required
def profile(id):
    user_lists = db.execute("SELECT list_name, id FROM list WHERE user_id = ?", id)
    name = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
    friendCheck = db.execute("SELECT * FROM friends WHERE user_id = ? AND friend_id = ?", session["user_id"], id)
    entries = []
    length = len(user_lists)
    for i in range(len(user_lists)):
        entries.append(len(db.execute("SELECT entry_id FROM entries WHERE list_id = ?", user_lists[i]["id"])))

    if len(friendCheck) > 0:
        isFriend = 1
        return render_template("index.html", user_lists=user_lists, id=int(id), name=name, isFriend=isFriend, entries=entries, length=length)
    else:
        isFriend = 0
        return render_template("index.html", user_lists=user_lists, id=int(id), name=name, isFriend=isFriend,entries=entries, length=length)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if not request.form.get("username"):
            error = 'Invalid username'
            return render_template("login.html", error=error)
        elif not request.form.get("password"):
            error = 'Invalid Password'
            return render_template("login.html", error=error)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = 'Incorrect username or password'
            return render_template("login.html", error=error)
        if error == None:
            flash('Succesfully logged in')
            session["user_id"] = rows[0]["id"]
            session["username"] = rows[0]["username"]
            return redirect("/")
    else:
        return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat_password = request.form.get("confirmation")

        check = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not username:
            error = 'Invalid username'
            return render_template('register.html', error=error)

        if username == "":
            error = 'Invalid username'
            return render_template('register.html', error=error)

        if len(check) != 0:
            error = 'Username already exists'
            return render_template('register.html', error=error)

        if not password:
            error = 'Invalid password'
            return render_template('register.html', error=error)

        if not repeat_password:
            error = 'Invalid passwords'
            return render_template('register.html', error=error)

        if password != repeat_password:
            error = 'Passwords must match'
            return render_template('register.html', error=error)
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/add", methods=["POST"])
def create_entry():
    
    req = request.get_json()
    rows = db.execute("SELECT * FROM entries WHERE entry_id = ? and list_id = ?",  req["id"], req["list_id"])
    if len(rows) != 0:
        return None    
    db.execute("INSERT INTO entries (entry_id, list_id, entry_type) VALUES (?, ?, ?)", req["id"], req["list_id"], req["entry_type"] )
    res = make_response(jsonify({"message": "JSON received"}), 200)
    return res

@app.route("/list", methods=["GET", "POST"])
def newList():
    if request.method == "POST":
        title = request.form.get('listName')
        db.execute("INSERT INTO list (list_name, user_id) VALUES (?, ?)", title, session["user_id"])
        id = db.execute("SELECT id FROM list WHERE list_name = ? AND user_id = ?", title, session["user_id"])
        return redirect("/list/" + str(id[0]['id']))
    else:
        return redirect("/")

@app.route("/list/<list_id>", methods=["GET", "POST"])
@login_required
def list(list_id):
    if request.method == "POST":
        title = request.form.get("search")
        return redirect("/search/movie/" + title)
    else: 
        title = db.execute("SELECT list_name FROM list WHERE id = ?", list_id)[0]["list_name"]
        user_id = db.execute("SELECT user_id FROM list WHERE id = ?", list_id)[0]["user_id"]
        entries = db.execute("SELECT * FROM entries WHERE list_id = ?", list_id)
        name = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
        entry_array = []
        entry_array_type = []
        for id in entries:
            try:
                if id["entry_type"] == 0:
                    url = f'https://api.themoviedb.org/3/movie/{id["entry_id"]}?api_key={API_KEY}&language=en-US'
                    entry_array_type.append(0)
                if id["entry_type"] == 1:
                    url = f'https://api.themoviedb.org/3/tv/{id["entry_id"]}?api_key={API_KEY}&language=en-US'
                    entry_array_type.append(1)
                response = requests.get(url)
                response.raise_for_status()
                
            except requests.RequestException:
                return None
            try:
                data = response.json()
                entry_array.append(data)
            except (KeyError, TypeError, ValueError):
                return None
            
        length = len(entry_array)
        return render_template("list.html", title=title, list_id = list_id, entry_array=entry_array, length=length, entry_array_type=entry_array_type, name=name, user_id=user_id)

@app.route("/delete", methods=["POST"])
def deleteItem():
    req = request.get_json()
    db.execute("DELETE FROM entries WHERE entry_id = ? AND list_id = ?", req["id"], req["list_id"])
    res = make_response(jsonify({"message": "JSON received"}), 200)
    return res  


@app.route("/check", methods=["POST"])
def checkItem():
    req = request.get_json()
    check = db.execute("SELECT * FROM entries WHERE entry_id = ? AND list_id = ?", req["id"], req["list_id"])
    if len(check) > 0:
        return "yes"
    return "no"


@app.route("/friends", methods=["POST", "GET"])
@login_required
def friends():
    if request.method == "POST":
        user = request.form.get('friendSearch')
        return redirect("/search/friends/" + user)

    else:
        friends = db.execute("SELECT * FROM friends WHERE user_id = ?", session["user_id"])
        length = len(friends)
        numberOfLists = []
        for i in range(length):
            numberOfLists.append(len(db.execute("SELECT list_name FROM list WHERE user_id = ?", friends[i]["friend_id"])))
        return render_template("friends.html", friends=friends, length=length, numberOfLists=numberOfLists)

@app.route("/search/friends/<name>", methods=["GET"])
@login_required
def searchFriend(name):
    userList = db.execute("SELECT * FROM users WHERE username LIKE ?", '%' + name + '%')
    friendsDict = db.execute("SELECT username FROM friends WHERE user_id = ?", session["user_id"])
    friends = []
    for i in range(len(friendsDict)):
        friends.append(friendsDict[i]["username"])
    numberOfLists = []
    for i in range(len(userList)):
        numberOfLists.append(len(db.execute("SELECT list_name FROM list WHERE user_id = ?", userList[i]["id"])))
    length = len(userList)
    return render_template("search.html", userList=userList, friends=friends, length=length, numberOfLists=numberOfLists, name=name)

@app.route("/addFriend", methods=["POST"])
def addFriend():
    req = request.get_json()
    db.execute("INSERT INTO friends (user_id, friend_id, username) VALUES (?, ?, ?)", session["user_id"], req["id"], req["username"])
    res = make_response(jsonify({"message": "JSON received"}), 200)
    return res

@app.route("/removeFriend", methods=["POST"])
def removeFriend():
    req = request.get_json()
    db.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", session["user_id"], req["id"])
    res = make_response(jsonify({"message": "JSON received"}), 200)
    return res


@app.route("/deleteList", methods=["POST"])
def deleteList():
    req = request.get_json()
    print(req)
    db.execute("DELETE FROM entries WHERE list_id = ?", req["id"])
    db.execute("DELETE FROM list WHERE id = ?", req["id"])
    res = make_response(jsonify({"message": "JSON received"}), 200)
    return res