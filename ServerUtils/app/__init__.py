from flask import Flask
import os

app = Flask(__name__)
# Connecting app with db.
app.config.update(dict(DATABASE = os.path.join(app.root_path, 'market.db')))
# Secret key for jwt tokens.
app.config['SECRET_KEY'] = "skfF142DFG3412alfjdjf421ADdiewfjvVDFGv42342nasfjsSFG231hjdf"

from app import views