from flask import Flask
 
app = Flask(__name__, static_folder='static')
 
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '27d4558b4f8e29373601a349c563f1c398e995f446b8015d'
app.config['JSON_AS_ASCII'] = False

from app import views  # noqa