import mysql.connector
#NOTE conn and cursor should be established before invoking the functions

# Establish a connection to the MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host='?_host', #TODO Add Credentials
        user='?_username',
        password='?_password',
        database='?_database'
    )

#Adding a new doctor
def add_doctor(doctorname, password, last_login): #TODO Add try/catch
    query = "INSERT INTO doctors (doctorname, password, last_login) VALUES (%s, %s, %s)"
    values = (doctorname, password, last_login)
    cursor.execute(query, values)
    conn.commit()
    print("Doctor added successfully.")

#Changing the last login time for a doctor
def change_last_login(doctor_id, new_last_login): #TODO Add try/catch
    query = "UPDATE doctors SET last_login = %s WHERE id = %s"
    values = (new_last_login, doctor_id)
    cursor.execute(query, values)
    conn.commit()
    print("Last login time updated successfully.")

#Adding a new patient
def add_patient(name, age, sex): #TODO Add try/catch
    query = "INSERT INTO patients (name, age, sex) VALUES (%s, %s, %s)"
    values = (name, age, sex)
    cursor.execute(query, values)
    conn.commit()
    print("Patient added successfully.")
    
# Retrieve a list of all patients
def get_all_patients(): #TODO Add try/catch
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    return patients

# Add a request
def add_request(doctor_id, patient_id, doctor_disease_id, status, date, ml_model_id):
    try:
        insert_query = """
        INSERT INTO requests (doctor_id, patient_id, doctor_disease_id, status, date, ml_model_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (doctor_id, patient_id, doctor_disease_id, status, date, ml_model_id)

        cursor.execute(insert_query, values)
        conn.commit()

        print("Request added successfully.")

    except Exception as e:
        print("Error adding request:", str(e))
        

# Get patient ID by patient name
def get_patient_id_by_name(patient_name):
    query = "SELECT id FROM patients WHERE name = %s"
    cursor.execute(query, (patient_name,))
    patient_id = cursor.fetchone()
    return patient_id

# Get doctor ID by doctor name
def get_doctor_id_by_name(doctor_name):
    query = "SELECT id FROM doctors WHERE doctorname = %s"
    cursor.execute(query, (doctor_name,))
    doctor_id = cursor.fetchone()
    return doctor_id

# Get disease ID by disease name
def get_disease_id_by_name(disease_name):
    query = "SELECT id FROM diseases WHERE disease_name = %s"
    cursor.execute(query, (disease_name,))
    disease_id = cursor.fetchone()
    return disease_id

# Get symptom ID by symptom name
def get_symptom_id_by_name(symptom_name):
    query = "SELECT id FROM symptoms WHERE symptom_name = %s"
    cursor.execute(query, (symptom_name,))
    symptom_id = cursor.fetchone()
    return symptom_id