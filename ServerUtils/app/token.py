from app import app
import jwt
from datetime import datetime, timedelta

def generate_token(user_id):
    token = jwt.encode({"user_id" : user_id, 
    "exp": datetime.utcnow() + timedelta(days=30)}, 
    app.config['SECRET_KEY'], algorithm = "HS256")
    return token

def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms = "HS256")
    except:
        return False