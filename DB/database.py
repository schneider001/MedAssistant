import mysql.connector


class Database:
    def __init__(self):

        config = { #TODO забирать эти данные из конфиг файла
            'user': 'root',
            'password': 'password123',
            'host': 'localhost',
            'database': 'MedAssistant',
            'raise_on_warnings': True
            }

        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
        self.execute_sql_script("../DB/create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи


    def execute_sql_script(self, script_file):
        try:
            with open(script_file, 'r') as file:
                sql_script = file.read()
                sql_commands = sql_script.split(';')
                for command in sql_commands:
                    if command.strip():
                        self.cursor.execute(command)
                self.conn.commit()
        except Exception as e:
            print(f"Error executing SQL script from file: {str(e)}") #TODO логировать ошибки, а не выводить на экран

    def select_doctor_by_id(self, id):
        query = "SELECT id, username, name, password_hash, last_login, is_blocked FROM doctors WHERE id = %s LIMIT 1"
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() #TODO добавить try/catch блок
        
    def select_doctor_by_username(self, username):
        query = "SELECT id, username, name, password_hash, last_login, is_blocked FROM doctors WHERE username = %s LIMIT 1"
        values = (username,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
        
    def insert_doctor_credentials(self, username, password_hash): #TODO использовать хэш пароля
        try:
            query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
            values = (username, password_hash)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Failed to insert doctor's credentials: {str(e)}")

    def close(self):
        self.cursor.close()
        self.conn.close()