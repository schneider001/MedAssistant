import mysql.connector
from hashlib import sha256

class Database:
    # Establish a connection to the MySQL database
    def __init__(self):

        config = { #TODO забирать эти данные из конфиг файла
            'user': 'medassist_user',
            'password': 'P@ssw0rd1',
            'host': 'db4free.net',
            'database': 'medassist_test',
            'raise_on_warnings': True
            }

        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
        #self.execute_sql_script("../DB/create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи

    # Establish MySQL database
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
        query = "SELECT id, username, password, last_login FROM doctors WHERE id = %s"
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() #TODO добавить try/catch блок
       

    # Adding a new doctor    
    def add_doctor_credentials(self, doctorname, password):
        try:
            query = "INSERT INTO doctors (username, password) VALUES (%s, %s)"
            values = (doctorname, sha256(password.encode('utf-8')).hexdigest())
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback() #db rolls back by itself generally
            print(f"Failed to insert doctor's credentials: {str(e)}")

    # Changing the last login time for a doctor
    def update_last_login(self, doctor_id): 
        try:
            query = "UPDATE doctors SET last_login = NOW() WHERE id = %s"
            values = (doctor_id)
            self.cursor.execute(query, (values,))
            self.conn.commit()
        except Exception as e:
            print(f"Failed to change last login time: {str(e)}")

    # Check if the provided doctor's password is correct, return id if successful
    def login_doctor_by_password(self, doctorname, password):

        query = "SELECT id FROM doctors WHERE username = %s AND password = %s"

        self.cursor.execute(query, (doctorname, sha256(password.encode('utf-8')).hexdigest()))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        return 0

    # Adding a new patient
    def add_patient(self, patientname, age, sex): 
        query = "INSERT INTO patients (name, age, sex) VALUES (%s, %s, %s)" #TODO Date of birth instead of age
        values = (patientname, age, sex)
        self.cursor.execute(query, values)
        self.conn.commit()     

    # Retrieve a list of all patients
    def get_all_patients(self): 
        self.cursor.execute("SELECT * FROM patients")
        patients = self.cursor.fetchall()
        return patients

    # Establish a doctor-patient relation
    def add_patient_to_doctor(self, doctor_id, *patient_ids):
        for patient_id in patient_ids:
            query = "INSERT INTO doctor_patients (doctor_id, patient_id) VALUES (%s, %s)"
            values = (doctor_id, patient_id)
            self.cursor.execute(query, values)
        self.conn.commit()
        
    # Get a list of available patients for a doctor by doctor ID
    def get_available_patients_for_doctor(self, doctor_id):

        query = """
        SELECT patients.id, patients.name, patients.age, patients.sex
        FROM patients
        INNER JOIN doctor_patients ON patients.id = doctor_patients.patient_id
        WHERE doctor_patients.doctor_id = %s
        """

        self.cursor.execute(query, (doctor_id,))
        available_patients = self.cursor.fetchall()

        return available_patients

    def close(self):
        self.cursor.close()
        self.conn.close()
