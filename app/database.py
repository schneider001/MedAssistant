import mysql.connector
import csv
from json import loads


from logs import Logs

class Database:
    def __init__(self):
        self.logger = Logs(__name__).get_logger()
        with open('../configs/db_settings.json', 'r') as options_file:
            config = loads(options_file.read())
        try:
            self.conn = mysql.connector.connect(**config) 
            self.logger.info('Database connection iniatedted successfully') 
        except mysql.connector.Error as e:
            self.logger.error('Database connection failed to iniate: %s', e)
            raise
        self.conn.autocommit = False 
    

    def execute_select(self, sql_query, *values, one_expected=False) -> list[tuple]:
        try:
            if not self.conn.is_connected():
                self.logger.info("Reconnecting to the database...")
                self.conn.reconnect()
            self.cursor = self.conn.cursor()
            self.cursor.execute(sql_query, values)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error("Failed to select from database: %s" 
                "\\\\query = %s \\\\values = %s", 
                str(e), sql_query, str(values))
            self.logger.exception(e)
        finally:
            self.cursor.close()
    
    
    def execute_update(self, sql_query, *values):
        try:
            if not self.conn.is_connected():
                self.logger.info("Reconnecting to the database...")
                self.conn.reconnect()
            self.cursor = self.conn.cursor()
            self.cursor.execute(sql_query, values)
            self.conn.commit()
            return self.cursor.lastrowid 
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Failed to update database: " + str(e) + \
                "\\\\query = " + sql_query + "\\\\values = " + str(values))
        finally:
            self.cursor.close()    
        

    #------------------------------------------
    #Doctors's queries
    #------------------------------------------
        
    #for testing
    def insert_doctor_credentials_(self, username, password_hash):
        query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
        self.execute_update(query, username, password_hash)
            
    #------------------------------------------
    #Patient's queries
    #------------------------------------------
    
    #for testing
    def insert_patient_(self, name, insurance_certificate, born_date):
        query = "INSERT INTO patients (name, insurance_certificate, born_date) VALUES (%s, %s, %s)"
        self.execute_update(query, name, insurance_certificate, born_date)


    #------------------------------------------
    #Close
    #------------------------------------------

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
            self.logger.info('Connection to database closed')
        except mysql.connector.Error as e: 
            self.logger.warning(f'Failed close connection to databbase: {e}')
            raise
