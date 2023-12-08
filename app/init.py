from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from datetime import datetime
import logging.config
from database import Database

ML_MODEL_VERSION = 'T_1.0'

logging.config.fileConfig('../configs/log.conf')

app = Flask(__name__)
app.static_folder = 'static'
app.config.update(SECRET_KEY = 'some secret key')

bcrypt = Bcrypt(app)
def gen_hashed_password(password : str):
    return bcrypt.generate_password_hash(password).decode('utf8')

def check_password_hash(hashed_password, password) :
    return bcrypt.check_password_hash(hashed_password, password)

db = Database()

login_manager = LoginManager(app)

socketio = SocketIO(app)

#import ml_model
import warnings
warnings.simplefilter("ignore")
import sys
sys.path.append('../ml_model')
from model import DiseasePredModel
ml_model = DiseasePredModel('../ml_model')
def get_disease(symptoms: list):
    
    max_symptoms_number = 17
    
    if len(symptoms) > max_symptoms_number:
        symptoms_to_model = symptoms[:max_symptoms_number]
    else:
        symptoms_to_model = symptoms + [float('nan')] * (max_symptoms_number - len(symptoms))

    return ml_model.predict(symptoms_to_model)[0]

