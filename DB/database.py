import mysql.connector
import csv
from json import loads
from hashlib import sha256
from DB.log_init import *

class Database:
    def __init__(self):

        with open('../configs/db_settings.json', 'r') as options_file:
            config = loads(options_file.read())
        try:
            self.conn = mysql.connector.connect(**config) 
            logger.info('Database connection iniatedted successfully') 
        except mysql.connector.Error as e:
            logger.warning(f'Database connection failed to iniate: {e}')
            raise
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
        self.execute_sql_script("../DB/create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи
        self.fill_from_dataset("../datasets/Symptom-severity.csv", "symptoms")
        self.fill_from_dataset("../datasets/symptom_Description.csv", "diseases")
        
    def execute_sql_script(self, script_file):
        with open(script_file, 'r') as file:
                sql_script = file.read()
                sql_commands = sql_script.split(';')
                try:
                    for command in sql_commands:
                        if command.strip():
                            self.cursor.execute(command)
                    self.conn.commit()
                    logger.info('Database created successfully')
                except mysql.connector.Error as e:
                    logger.warning(f'Database failed to create: {e}')
                    self.conn.rollback()
                    raise

    def fill_from_dataset (self, filepath, tablename):
        data_set = set()
        with open(filepath, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                data_set.add(row[0])
        try:
            for entry in data_set:
                query = f"INSERT IGNORE INTO {tablename} (name) VALUES (%s)"
                values = (entry,)
                self.cursor.execute(query, values)      
            self.conn.commit()
            logger.info(f'Information about {tablename} added successfully to database')
        except mysql.connector.Error as e:
            self.conn.rollback()
            logger.warning(f'Information about {tablename} failed to add to database: {e}')
            raise

    def select_doctor_by_id(self, id):
        query = "SELECT id, username, name, password_hash, last_login, \
            is_blocked, image_path_location FROM doctors WHERE id = %s"
        values = (id,)
        try:
            self.cursor.execute(query, values)
            logger.info('Fetched doctor info by id successfully')
        except mysql.connector.Error as e:
            logger.warning(f'Failed to fetch doctor info by id: {e}')
            raise
        return self.cursor.fetchone()

    def select_doctor_by_username(self, username):
        query = "SELECT id, username, name, password_hash, last_login, is_blocked FROM doctors WHERE username = %s" 
        values = (username,)
        try:
            self.cursor.execute(query, values)
            logger.info('Fetched doctor info by username successfully')
        except mysql.connector.Error as e:
            logger.warning(f'Failed to fetch doctor info by username: {e}')
            raise
        return self.cursor.fetchone()

    def insert_doctor_credentials(self, username, password_hash): #TODO использовать хэш пароля
        query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
        values = (username, password_hash)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            logger.info(f'Inserted doctor info {username}:{password_hash} successfully')
        except mysql.connector.Error as e:
            self.conn.rollback()
            logger.warning(f'Failed to insert doctor info: {e}')
            raise

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
            logger.info('Connection to database closed')
        except mysql.connector.Error as e: 
            logger.warning(f'Failed close connection to databbase: {e}')
            raise
