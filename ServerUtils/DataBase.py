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
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM User_Info WHERE mail LIKE '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('already exists')
                return {'error':'User already exists'}

            self.__cur.execute(f"INSERT INTO User_Info (name, mail, password) VALUES('{name}', '{mail}', '{hpsw}')")
            self.__db.commit()
            self.__cur.execute(f"SELECT id FROM User_Info WHERE mail LIKE '{mail}'")
            res = self.__cur.fetchone()
            return {'id':res}

        except sqlite3.Error:
            print("Пизда базе при внесении юзера")
            return {'error':'DataBase Error'}

    def get_account(self, mail, psw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM User_Info WHERE mail LIKE '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] != 1:
                print('No user')
                return {'error':'User doesnt exists'}

            self.__cur.execute(f"SELECT * FROM User_Info WHERE mail LIKE '{mail}'")
            res = self.__cur.fetchone()
            if check_password_hash(res['password'], psw):
                return {'id':f'{res["id"]}'}
            else:
                return {'error':'Wrong password'}

        except sqlite3.Error:
            print("Пизда базе при получении юзера")
            return {'error':'DataBase Error'}

    def search_items(self, request_string):
        try:
            #формируем из строки запроса список из слов в запросе и обрезаем их, оставляя первые 4 буквы
            request_list = [x[:4] for x in request_string.split(' ') if len(x) > 4 and x.isalpha()]

        except sqlite3.Error:
            print("Пизда базе при поиске товара")
            return {'error':'DataBase Error'}


