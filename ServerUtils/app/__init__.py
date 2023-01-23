from flask import Flask
import os

app = Flask(__name__)
# connecting app with db
app.config.update(dict(DATABASE = os.path.join(app.root_path, 'market.db')))

from app import views