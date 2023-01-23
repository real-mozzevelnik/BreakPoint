import sqlite3
from werkzeug.security import check_password_hash

def cut_for_search(string):
    return string[:4]

class DataBase():
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()


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
            self.__cur.execute(f"SELECT id FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            return {'id':res['id'], 'error':0}

        except sqlite3.Error:
            return {'error':'DataBase Error'}


    def get_account(self, mail, psw):
        try:
            # check if user exists
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] != 1:
                return {'error':'User doesnt exists'}

            self.__cur.execute(f"SELECT * FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()

            # check password
            if check_password_hash(res['password'], psw):
                return {'id':res['id'], 'error':0}
            else:
                return {'error':'Wrong password'}

        except sqlite3.Error:
            return {'error':'DataBase Error'}


    def search_items(self, request_string):
        try:
            #формируем из строки запроса список из слов в запросе и обрезаем их, оставляя первые 4 буквы
            request_list = [x[:4] for x in request_string.split(' ') if len(x) > 4 and x.isalpha()]

        except sqlite3.Error:
            return {'error':'DataBase Error'}


