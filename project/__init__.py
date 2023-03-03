from subprocess import Popen
from os.path import exists

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "JGNjgN;853s@#$^@9_^%$&*#384"
uri = 'sqlite:///../database/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
data = []
listener = Popen(['python', 'project/socket_server.py'])


from project import routers
from project import forms
from project import models


file = open('console-data.txt', 'w')
file.close()


db.create_all()
user = models.User.query.filter_by(username='administrator').first()
if not user:
    user = models.User(username='administrator', password=generate_password_hash('123456789'))
    db.session.add(user)
    db.session.commit()
