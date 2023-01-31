import sqlite3
from werkzeug.security import check_password_hash
from app.search_utils import brands, colors, types

class DataBase():
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    
    def does_user_exists(self, id):
        self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE id = '{id}'")
        res = self.__cur.fetchone()
        return {'error':'User doesnt exists'} if not res['count'] else {'error':0}


    def add_user(self, name, mail, hpsw):
        try:
            # check if user exists
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return {'error':'User already exists'}

            # create new user in db
            self.__cur.execute(f"INSERT INTO Users (name, mail, password) VALUES('{name}', '{mail}', '{hpsw}')")
            self.__db.commit()
            self.__cur.execute(f"SELECT user_id FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            return {'id':res['user_id'], 'error':0}

        except sqlite3.Error:
            return {'error':'DataBase Error'}


    def get_account(self, mail, psw):
        try:
            # check if user exists
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] != 1:
                return {'error':'User doesnt exists'}

            self.__cur.execute(f"SELECT user_id, password FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()

            # check password
            if check_password_hash(res['password'], psw):
                return {'id':res['user_id'], 'error':0}
            else:
                return {'error':'Wrong password'}

        except sqlite3.Error:
            return {'error':'DataBase Error'}


    def search_items(self, request_string, item_counter):
        try:
            item_brand = ""
            item_color = ""
            item_type = ""
            request_list = request_string.lower().split(" ")
            # iterate for every word in request and sort it
            for param in request_list:
                if param in brands:
                    item_brand = param
                elif param in colors:
                    item_color = param
                elif param in types:
                    item_type = param

            self.__cur.execute(f"""SELECT item_id, name, price, main_photo_src FROM Items 
                WHERE category LIKE '{item_type}%' AND main_color LIKE '{item_color}%' AND brand LIKE '{item_brand}%'
                LIMIT {item_counter}, 10""")

            res = self.__cur.fetchall()
            items_to_send = []
            for i, _ in enumerate(res):
                items_to_send.append(list(res[i]))
                
            return {"items":items_to_send, "error":0, "item_counter":len(items_to_send)}

        except sqlite3.Error:
            return {'error':'DataBase Error'}


