from flask import Flask, request, g, jsonify
import json
import sqlite3
import os
from DataBase import DataBase
from werkzeug.security import generate_password_hash

ip = '127.0.0.1'

DATABASE = 'market.db'
DEBUG = True
SECRET_KEY = 'jsdfjhdhe2uy4y3yr2872hgfgh93hf73y3yr23r72yh2373'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE = os.path.join(app.root_path, 'market.db')))

dbase = None

#соединение с базой
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory =  sqlite3.Row
    return conn

#создание базы, не юзай блять с сервером
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    # соединение, если оно еще не установленно
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

#закрыть базу автоматом
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

#получить базу до каждого реквеста
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = DataBase(db)

#блок входа пользователя, возвращет id пользователя
@app.route('/authorization', methods = ["POST", "GET"])
def authorization():
    if request.method == 'POST':
        content = request.json
        res = dbase.get_account(content['mail'], content['psw'])

    return jsonify(res)

#блок регистрации пользователя, возвращет id пользователя
@app.route('/registration', methods = ["POST", "GET"])
def registration():
    if request.method == 'POST':
        content = request.json
        # print(content['psw'])
        hash = generate_password_hash(content['psw'])
        res = dbase.add_user(content['name'], content['mail'], hash)

    return jsonify(res)

@app.route('/search', methods = ["POST", "GET"])
def search():
    if request.method == 'POST':
        content = request.json
        res = dbase.search_items(content['request_string'])

    return jsonify(res)

if __name__=='__main__':
    app.run(debug = DEBUG, host = ip)

# '192.168.110.21:5000/registration'