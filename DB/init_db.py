import mysql.connector
from db_operations import connect_to_database()

# Establish a connection to the MySQL database
conn = connect_to_database()

# Create a cursor to execute queries
cursor = conn.cursor()

# Specify the path to your SQL script file
sql_script_file = './DB/create_db_script.sql'

# Read and execute the SQL script
try:
    with open(sql_script_file, 'r') as script_file:
        sql_script = script_file.read() #TODO Check if database exists, add AUTOINCREMENT to id's
        cursor.execute(sql_script, multi=True)
    conn.commit()
    print("SQL script executed successfully.")
except Exception as e:
    print("Error executing SQL script:", str(e))
    
    

# Close the cursor and connection when done
cursor.close()
conn.close()