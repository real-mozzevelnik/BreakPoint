from flask import Flask
import os

from app.config import SECRET_KEY

app = Flask(__name__)
# Connecting app with db.
app.config.update(dict(DATABASE = os.path.join(app.root_path, 'db/market.db')))
# Secret key for jwt tokens.
app.config['SECRET_KEY'] = SECRET_KEY

from app import views