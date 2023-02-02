from flask import Flask
import os

app = Flask(__name__)
# connecting app with db
app.config.update(dict(DATABASE = os.path.join(app.root_path, 'market.db')))
app.config['SECRET_KEY'] = "skfF142DFG3412alfjdjf421ADdiewfjvVDFGv42342nasfjsSFG231hjdf"

from app import views