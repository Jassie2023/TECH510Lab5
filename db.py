
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv('DB_USER', 'serverloginname') 
db_pw = os.getenv('DB_PASSWORD', 'A123456#')  
db_host = os.getenv('DB_HOST', 'techin510lab4.postgres.database.azure.com')  
db_port = os.getenv('DB_PORT', '5432') 
db_name = os.getenv('DB_NAME', 'postgres')
conn_str = f'postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}'

# print(db_user, db_pw, db_host, db_port, db_name)

def get_db_conn():
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    return conn
