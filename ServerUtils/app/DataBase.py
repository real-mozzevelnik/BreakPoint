import sqlite3
from werkzeug.security import check_password_hash
from app.search_utils import brands, colors, types
from email_validator import validate_email, EmailNotValidError


# Class for interaction with database.
class DataBase():
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()


    # Method for checking if user with given id exists in db.
    # The reason it is used is that user have ability to enter his account from
    # different devices. That way he can delete his account from one device and try to enter from
    # another one. When user opens the app, frontend sends the server request to check if that user still exists.
    # If he doenst exists in db frontend redirects user to registration/authentication page.
    def does_user_exists(self, id):
        self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE id = '{id}'")
        res = self.__cur.fetchone()
        return {'error':'User doesnt exists'} if not res['count'] else {'error':0}


    # Method for adding new one user.
    # Checks if user with such mail already exists.
    # Db contains user password using hash.
    def add_user(self, name, mail, hpsw):
        try:
            # Check if email is valid.
            validate_email(mail)
            # Check if user exists.
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return {'error':'User already exists'}

            # Create new user in db.
            self.__cur.execute(f"INSERT INTO Users (name, mail, password) VALUES('{name}', '{mail}', '{hpsw}')")
            self.__db.commit()
            # Send back user_id, so frontend can save it and send it to server for another types of requests.
            self.__cur.execute(f"SELECT user_id FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            return {'user_id':res['user_id'], 'error':0}

        # If given email isnt valid it will raise an error, according
        # to the app architecture it has to be handled that way.
        except EmailNotValidError:
            return {'error':'Not valid email'}
        except sqlite3.Error:
            return {'error':'DataBase Error'}


    # Method to authenticate the user.
    # Checks if user with given mail exists, 
    # compares given password with password from db.
    # Returns user id.
    def get_account(self, mail, psw):
        try:
            # Check if user with given mail exists in db.
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] != 1:
                return {'error':'User doesnt exists'}

            # Get id and password from db.
            self.__cur.execute(f"SELECT user_id, password FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()

            # Check password and return id.
            return {'user_id':res['user_id'], 'error':0} if check_password_hash(res['password'], psw) else {'error':'Wrong password'}

        except sqlite3.Error:
            return {'error':'DataBase Error'}

    # Method to parse given string and search for requested items in db.
    # Returns dict that include array of items(dicts that contains info),
    # error, and number of sended items.
    def search_items(self, request_string, item_counter):
        try:
            # Initialize the strings for sql request.
            # The reason it is necessary is that if there will be none of these parameters
            # in string, sql request still gonna work.  
            item_brand = ""
            item_color = ""
            item_type = ""
            request_list = request_string.lower().split(" ")
            # Iterate for every word in request and sort it.
            for param in request_list:
                if param in brands:
                    item_brand = param
                elif param in colors:
                    item_color = param
                elif param in types:
                    item_type = param

            # Sql request to get necessary info such as id, price, name and main photo.
            # Db contains src for photos, photos located in google firebase storage.
            # Reason LIMIT is used is that it is not well to send all the itens to frontend.
            # Item counter is the number that stored in frontend.
            # At the beggining of scrolling that equals to 0.
            # After that server returns list of items and number of returned items.
            # Frontend adds this number to the previos value of item counter. 
            # When user will scroll down the given items, frontend sends new one request for items
            # and send his items counter.
            # But server has to give new items to user, so start of the searching depends on item counter.
            self.__cur.execute(f"""SELECT item_id, name, price, main_photo_src FROM Items 
                WHERE category LIKE '{item_type}%' AND main_color LIKE '{item_color}%' AND brand LIKE '{item_brand}%'
                LIMIT {item_counter}, 10""")

            res = self.__cur.fetchall()
            # Array for items.
            items_to_send = []
            # Make dict for every item and add it to final array.
            for i, _ in enumerate(res):
                tmp = list(res[i])
                tmp_dict = {"item_id":tmp[0], "name":tmp[1], "price":tmp[2], "main_photo_src":tmp[3]}
                items_to_send.append(tmp_dict)
                
            return {"items":items_to_send, "error":0, "item_counter":len(items_to_send)}

        except sqlite3.Error:
            return {'error':'DataBase Error'}

     
    def get_item(self, item_id):
        try:
            self.__cur.execute(f"""SELECT sizes, photo_src FROM Items INNER JOIN Photos 
                ON Items.item_id = Photos.item_id WHERE Items.item_id = {item_id}""")
            res = self.__cur.fetchall()

            sizes = res[0]['sizes'].split(" ")
            photos = [res[0]['photo_src'], res[1]['photo_src']]

            return {"sizes":sizes, "photos":photos}
            
        except sqlite3.Error:
            return {'error':'DataBase Error'}


