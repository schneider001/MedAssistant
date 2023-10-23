from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from datetime import datetime


import sys
sys.path.append("..")

from DB.database import Database

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



#for testing
db.insert_doctor_credentials("Petrovich", gen_hashed_password("simple_password")) #для теста login_post
db.insert_patient_("Иван Петрович Рыбаков", "123-43-234 23", datetime(1990, 10, 23))
db.insert_patient_("Гавриил Дмитрич Сплюев", "457-56-234 76", datetime(2001, 8, 29))
db.insert_patient_("Биба Бобович Кончин", "654-43-928 25", datetime(1953, 12, 30))


