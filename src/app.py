from flask import Flask
from os import getenv

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 2*1024*1024

import routes



