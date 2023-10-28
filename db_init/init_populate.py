import json
import string
from csv import reader
from json import loads
from os import system
from datetime import datetime, timedelta
from random import randint, random, choice, sample

with open('../configs/db_settings.json', 'r') as options_file:
	data=json.load(options_file)

USERNAME = data['user']
PASSWORD = data['password']
DBNAME = data['database']
FILE = "create_db_script.sql"
file_command = """mysql -u %s -p"%s" %s < %s""" %(USERNAME, PASSWORD, DBNAME, FILE)
single_command = """mysql -u %s -p"%s" %s --execute=""" %(USERNAME, PASSWORD, DBNAME)
query_line=""
def purge_create_database():
    try:
        system(file_command)
    except Exception as e:
        print(f"Unable to create database: {e}")

def fill_from_dataset (filepath, tablename):
    data_set = set()
    global query_line
    with open(filepath, 'r') as csv_file:
        _reader = reader(csv_file)
        header = next(_reader)
        for row in _reader:
            if row[0] not in data_set:
                data_set.add(row[0])
                query = f"INSERT  INTO {tablename} (name, ru_name) VALUES ('{row[0]}', '{row[2]}')"
                query_line+=query
                query_line+=';'

def fill_sympt_diseases():
    fill_from_dataset("../datasets/Symptom-severity_ru.csv", "symptoms")
    fill_from_dataset("../datasets/symptom_Description_ru.csv", "diseases")
    system(single_command+'"'+query_line+'"')

def get_random_timestamp():
    return f"'{datetime.now() - random() * timedelta(weeks=2000)}'"

def get_random_snils():
    return f"'{randint(100, 999)}-{randint(10, 99)}-{randint(100, 999)} {randint(10, 99)}'"
    
def get_random_string(length = 10):
    letters = string.ascii_lowercase
    return f"'{''.join(choice(letters) for i in range(length))}'"

def populate_database(): #использовать db методы в идеале
    global query_line
    query_line = ""
    people = [
    ("'Иванов Иван Иванович'", get_random_snils(), get_random_timestamp(), 1),
    ("'Петров Петр Петрович'", get_random_snils(), get_random_timestamp(), 2),
    ("'Сидоров Сидор Сидорович'", get_random_snils(), get_random_timestamp(), 1),
    ("'Алексеев Алексей Алексеевич'", get_random_snils(), get_random_timestamp(), 2),
    ("'Дмитриев Дмитрий Дмитриевич'", get_random_snils(), get_random_timestamp(), 1)
    ]
    doctors = [
    ("'doctor1'", "'Николаев Николай Николаевич'", "'$2b$12$pT14zDz8TEpMRxJpo491L.Qmaof0UINo4zfl.b6yVU5PaMXeg4Dvu'", get_random_timestamp()), #hash pwd - 1
    ("'doctor2'", "'Васильев Василий Васильевич'", "'$2b$12$L0biwxV8iz7bkVCSUJm.1ucN9DuSuZJx9j8YXJOWOJL5qhfOOZB0O'", get_random_timestamp()), #hash pwd - 2 etc.
    ("'doctor3'", "'Андреев Андрей Андреевич'", "'$2b$12$KEW63xUmE.DV5JA/WuRz3..Rne26Se9imQuYB9koWqrduxs2Qud/O'"),
    ("'doctor4'", "'Сергеев Сергей Сергеевич'", "'$2b$12$KEW63xUmE.DV5JA/WuRz3..Rne26Se9imQuYB9koWqrduxs2Qud/O'"),
    ("'doctor5'", "'Михайлов Михаил Михайлович'", "'$2b$12$KEW63xUmE.DV5JA/WuRz3..Rne26Se9imQuYB9koWqrduxs2Qud/O'", get_random_timestamp())
    ]
    admins = [
    ("'admin1'", "'Владимиров Владимир Владимирович'", "'$2b$12$NqbVgF7mOnrR.Tei.kNm2OfwdieVCYgNrhdit8FEv7f8xCawI6jrm'"), #123
    ("'admin2'", "'Егоров Егор Егорович'", "'$2b$12$Fua24yccL/0O.OWfMtdobed0EZiyRQofaS2qG2/PWKIYCKf/of8qW'") #321
    ]
    
    for person in people:
        query = f"INSERT INTO patients (name, insurance_certificate, born_date, sex) VALUES ({person[0]}, {person[1]}, {person[2]}, {person[3]})"
        query_line+=query
        query_line+=';'
        
    for person in doctors:
        query = f"INSERT INTO doctors (username, name, password_hash, last_login) VALUES ({person[0]}, {person[1]}, {person[2]}, {person[3] if len(person)>3 else 'NULL'})"
        query_line+=query
        query_line+=';'
        
    for person in admins:
        query = f"INSERT INTO administrators (username, name, password_hash) VALUES ({person[0]}, {person[1]}, {person[2]})"
        query_line+=query
        query_line+=';'
        
    for x in range(10):
        query = f"INSERT INTO requests (doctor_id, patient_id, status, date) VALUES ({randint(1, 5)}, {randint(1, 5)}, {randint(1, 3)}, {get_random_timestamp()})"
        query_line+=query
        query_line+=';'
        for symt_num in range(randint(1, 6)):
            query = f"INSERT INTO request_symptoms (symptom_id, request_id) VALUES ({randint(1, 130)}, {x+1})" #an error may arise with a small probability
            query_line+=query
            query_line+=';'
            rand_arr = sample(range(1, 5), 3)
        for comm_num in range(randint(0, 3)):
            query = f"INSERT INTO comments (doctor_id, request_id, comment) VALUES ({rand_arr[comm_num]}, {x+1}, {get_random_string(25)})" 
            query_line+=query
            query_line+=';'
        
    system(single_command+'"'+query_line+'"')
        
                    
purge_create_database()
fill_sympt_diseases()
populate_database()