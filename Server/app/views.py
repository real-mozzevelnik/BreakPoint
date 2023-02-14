from werkzeug.security import generate_password_hash
from flask import request, g, jsonify
import sqlite3

from app.database import Database
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
    dbase = Database(db)


# Close the connection after every request.
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


# User authorization. Returns user id, error.
# Needs mail and password passed in json.
@app.route('/login', methods = ["POST"])
def login():
    content = request.json
    res = dbase.retrieve_account(content['mail'], content['psw'])

    return jsonify(res)


# User registration. Returns user id, error.
# Needs user name, mail and password passed in json.
@app.route('/registr', methods = ["POST"])
def registr():
    content = request.json
    hash = generate_password_hash(content['psw'])
    res = dbase.create_user(content['name'], content['mail'], hash)

    return jsonify(res)

# Used for searching for required items.
# Needs request string and number of items already displayed passed in json.
@app.route('/search', methods = ["POST"])
def search():
    content = request.json
    res = dbase.search_items(content['request_string'], content['item_counter'])

    return jsonify(res)


# When user taps the item icon, server has to send part of info about item.
# Needs item id
@app.route('/item', methods = ["POST"])
def item():
    content = request.json
    res = dbase.retrieve_item(content['item_id'])

    return jsonify(res)


# Route for checking if user with given id inside token exists in db.
# The reason it is used is that user have ability to enter his account from
# different devices. That way he can delete his account from one device and try to enter from
# another one. When user opens the app, frontend sends the server request to check if that user still exists.
# If he doenst exists in db frontend redirects user to registr/login page.
@app.route('/does_exists', methods = ['POST'])
def does_exists():
    content = request.json
    res = dbase.does_user_exists(content['access_token'])

    return jsonify(res)


# Interacion with cart (add and delete).
# Needs access token, item id, size.
@app.route('/cart', methods = ['POST', 'DELETE'])
def cart():
    content  = request.json
    res = dbase.update_cart(content['access_token'], content['item_id'], 
        content['size'], request_type = request.method)
    
    return jsonify(res)


# Viewing the shopping cart.
# Needs access token and item counter.
@app.route('/show_cart', methods = ['POST'])
def show_cart():
    content = request.json
    res = dbase.retrieve_cart(content['access_token'], content['item_counter'])

    return jsonify(res)


# User info interaction.
# Use POST if user changes his name or mail.
# Use DELETE to delete user.
# If user only wants to change mail, but not name,
# frontend still has to send "name" and put here just the name user has now.
# That way it works with changing only name.
# For deletion user frontend sends name and mail user has now.
@app.route('/update_user', methods = ['POST', 'DELETE'])
def update_user():
    content = request.json
    res = dbase.update_user_info(content['access_token'], content['new_mail'], 
        content['new_name'], request_type = request.method)

    return jsonify(res)