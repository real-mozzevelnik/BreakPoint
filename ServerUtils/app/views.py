from werkzeug.security import generate_password_hash
from flask import request, g, jsonify
import sqlite3

from app.DataBase import DataBase
from app import app

dbase = None


# connecting to the database
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory =  sqlite3.Row
    return conn


# !creating databse, use in terminal
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    # connection, if it doesnt connected yet
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# connect to database before every request
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = DataBase(db)


# close the connection after every request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


# user authorization, returns user id
@app.route('/authorization', methods = ["POST"])
def authorization():
    if request.method == 'POST':
        content = request.json
        res = dbase.get_account(content['mail'], content['psw'])

    return jsonify(res)


# user registration, returns user id
@app.route('/registration', methods = ["POST"])
def registration():
    if request.method == 'POST':
        content = request.json
        hash = generate_password_hash(content['psw'])
        res = dbase.add_user(content['name'], content['mail'], hash)

    return jsonify(res)

# used for searching for items
@app.route('/search', methods = ["POST"])
def search():
    if request.method == 'POST':
        content = request.json
        res = dbase.search_items(content['request_string'])

    return jsonify(res)