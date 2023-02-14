import sqlite3
from werkzeug.security import check_password_hash
from email_validator import validate_email, EmailNotValidError

from app.item_utils import brands, colors, types, pack_items
from app.token import generate_token, decode_token

# Class for interaction with database.
class Database():
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()


    # Method for checking if user with given id inside token exists in db.
    # The reason it is used is that user have ability to enter his account from
    # different devices. That way he can delete his account from one device and try to enter from
    # another one. When user opens the app, frontend sends the server request to check if that user still exists.
    # If he doenst exists in db frontend redirects user to registr/login page.
    def does_user_exists(self, access_token):
        # Check if token is valid.
        jwt_data = decode_token(access_token)
        if not jwt_data:
            return {'error' : 'Invalid token'}

        user_id = jwt_data['user_id']
        # Check if user exists in db.
        self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE user_id = '{user_id}'")
        res = self.__cur.fetchone()
        # Nothing to return if user exists(success).
        return {'error' : 'User doesnt exists'} if not res['count'] else {}


    # Method for adding new one user.
    # Checks if user with such mail already exists.
    # Db contains user password using hash.
    # Returns user id, name, male and expiration time in token.
    def create_user(self, name, mail, hpsw):
        try:
            # Check if email is valid.
            validate_email(mail)
            # Check if user exists.
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return {'error' : 'User already exists'}

            # Create new user in db.
            self.__cur.execute(f"INSERT INTO Users (name, mail, password) VALUES('{name}', '{mail}', '{hpsw}')")
            self.__db.commit()
            # Send back data inside token, so frontend can save it and send it to server for another types of requests.
            self.__cur.execute(f"SELECT user_id FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            access_token = generate_token(res['user_id'], mail, name)
            return {'access_token' : access_token}

        # If given email isnt valid it will raise an error, according
        # to the app architecture it has to be handled that way.
        except EmailNotValidError:
            return {'error' : 'Not valid email'}
        except sqlite3.Error:
            return {'error' : 'DataBase Error'}


    # Method to authenticate the user.
    # Checks if user with given mail exists, 
    # compares given password with password from db.
    # Returns user id, name, male and expiration time in token.
    def retrieve_account(self, mail, psw):
        try:
            # Check if user with given mail exists in db.
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()
            if res['count'] != 1:
                return {'error' : 'User doesnt exists'}

            # Get id and password from db.
            self.__cur.execute(f"SELECT user_id, name, password FROM Users WHERE mail = '{mail}'")
            res = self.__cur.fetchone()

            # Check password and return data inside token.
            access_token = generate_token(res['user_id'], mail, res['name'])
            return {'access_token' : access_token} if check_password_hash(res['password'], psw) else {'error' : 'Wrong password'}

        except sqlite3.Error:
            return {'error' : 'DataBase Error'}

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
                LIMIT {item_counter}, 14""")

            res = self.__cur.fetchall()

            return pack_items(res)

        except sqlite3.Error:
            return {'error' : 'DataBase Error'}

    
    # Method to get item info from db.
    def retrieve_item(self, item_id):
        try:
            # Get sizes and photo src from db.
            self.__cur.execute(f"""SELECT sizes, photo_src FROM Items INNER JOIN Photos 
                ON Items.item_id = Photos.item_id WHERE Items.item_id = {item_id}""")
            res = self.__cur.fetchall()

            # Sizes are contained in db as text (example - 'XS S M L XS').
            # That way server splits the sizes into array of strings.
            sizes = res[0]['sizes'].split(" ")
            # Make an arrar from photo src
            photos = [res[0]['photo_src'], res[1]['photo_src']]

            return {"sizes" : sizes, "photos" : photos}
            
        except sqlite3.Error:
            return {'error' : 'DataBase Error'}


    # Method for interation with cart (add and delete).
    def update_cart(self, access_token, item_id, size, request_type):
        try:
            # Check if token is valid.
            jwt_data = decode_token(access_token)
            if not jwt_data:
                return {'error' : 'Invalid token'}

            # Get user_id from token.
            user_id = jwt_data['user_id']

            # Check if item with given size is in cart.
            self.__cur.execute(f"""SELECT COUNT() as 'count' FROM Cart WHERE user_id = '{user_id}'
                AND item_id = '{item_id}' AND size = '{size}'""")
            res = self.__cur.fetchone()

            # If it was POST request, add item to cart.
            if request_type == 'POST':
                # Check if item does not exist yet.
                if res['count'] != 0:
                    return {'error' : 'already in cart'}

                # Insert info in cart table.
                # Table also contains time of adding, that way items could be sorted
                # when user checks his cart.
                self.__cur.execute(f"""INSERT INTO Cart (user_id, item_id, add_time, size) 
                    VALUES('{user_id}', '{item_id}', datetime('now'), '{size}')""")

            # If it was DELETE request, delete item from cart.
            elif request_type == 'DELETE':
                # Check if item exists in cart.
                if res['count'] != 1:
                    return {'error' : 'not in cart'}

                # Delete item.
                self.__cur.execute(f"""DELETE FROM Cart WHERE user_id = '{user_id}'
                    AND item_id = '{item_id}' AND size = '{size}'""")

            # Commit changes.
            self.__db.commit()
            
            # Nothing to return (success).
            return {}

        except sqlite3.Error:
            return {'error' : 'DataBase Error'}


    # Method to get cart for current user.
    def retrieve_cart(self, access_token, item_counter):
        try:
            # Check if token is valid.
            jwt_data = decode_token(access_token)
            if not jwt_data:
                return {'error' : 'Invalid token'}

            # Get user_id from token.
            user_id = jwt_data['user_id']

            # Get requested info.
            # Logic for item_counter described in comments for "search_items" method.
            self.__cur.execute(f"""SELECT Items.item_id, name, price, main_photo_src, size FROM Items INNER JOIN Cart
                    ON Items.item_id = Cart.item_id WHERE Cart.user_id = '{user_id}' LIMIT {item_counter}, 14""")

            res = self.__cur.fetchall()
            
            return pack_items(res, add_size=True)

        except sqlite3.Error:
            return {'error' : 'DataBase Error'}


    # Method to update or delete user.
    def update_user_info(self, access_token, new_mail, new_name, request_type):
        try:
            # Check if token is valid.
            jwt_data = decode_token(access_token)
            if not jwt_data:
                return {'error' : 'Invalid token'}

            # Get user_id from token.
            user_id = jwt_data['user_id']

            # Update info.
            if request_type == 'POST':
                self.__cur.execute(f"""UPDATE Users SET mail = '{new_mail}', name = '{new_name}'
                    WHERE user_id = '{user_id}'""")

            # Delete user.
            elif request_type == 'DELETE':
                self.__cur.execute(f"""DELETE FROM Users WHERE user_id = {user_id}""")
                self.__cur.execute(f"""DELETE FROM Cart WHERE user_id = {user_id}""")

            # Commit changes.
            self.__db.commit()
            
            # Nothing to return (success).
            return {}

        except sqlite3.Error:
            return {'error' : 'DataBase Error'}
