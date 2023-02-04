from app import app
import jwt
from datetime import datetime, timedelta

# Create access token.
# Token contains user id, name, mail and expiration time.
def generate_token(user_id, mail, name):
    token = jwt.encode({"user_id" : user_id, "mail" : mail,
    "name" : name, "exp": datetime.utcnow() + timedelta(days=30)}, 
    app.config['SECRET_KEY'], algorithm = "HS256")
    return token

# If token cannot be decoded with secret key, that means token isnt valid.
# It will raise an exception and return False.
def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms = "HS256")
    except:
        return False