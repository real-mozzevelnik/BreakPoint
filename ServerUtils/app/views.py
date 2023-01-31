from werkzeug.security import generate_password_hash
from flask import request, g, jsonify
import sqlite3

from app.DataBase import DataBase
from app import app

dbase = None


# Connecting to the database.
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory =  sqlite3.Row
    return conn


# Set up connection with db, if it doesnt connected yet.
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# Connect to database before every request.
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = DataBase(db)


# Close the connection after every request.
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


# User authorization. Returns user id, error.
# Needs mail and password passed in json.
@app.route('/authentication', methods = ["POST"])
def authentication():
    if request.method == 'POST':
        content = request.json
        res = dbase.get_account(content['mail'], content['psw'])

    return jsonify(res)


# User registration. Returns user id, error.
# Needs user name, mail and password passed in json.
@app.route('/registration', methods = ["POST"])
def registration():
    if request.method == 'POST':
        content = request.json
        hash = generate_password_hash(content['psw'])
        res = dbase.add_user(content['name'], content['mail'], hash)

    return jsonify(res)

# Used for searching for required items.
# Needs request string and number of items already displayed passed in json.
@app.route('/search', methods = ["POST"])
def search():
    if request.method == 'POST':
        content = request.json
        res = dbase.search_items(content['request_string'], content['item_counter'])

    return jsonify(res)