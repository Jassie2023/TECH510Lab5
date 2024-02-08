import psycopg2
import os

def get_db_conn():
    db_user = os.getenv('DB_USER', 'serverloginname') 
    db_pw = os.getenv('DB_PASSWORD', 'A123456#')  
    db_host = os.getenv('DB_HOST', 'techin510lab4.postgres.database.azure.com')  
    db_port = os.getenv('DB_PORT', '5432') 
    db_name = os.getenv('DB_NAME', 'postgres')

    conn_str = f'postgresql://{db_user}:{db_pw}@{db_host}/{db_name}'
    return psycopg2.connect(conn_str)

def create_events_table():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL UNIQUE,
        date TIMESTAMP WITH TIME ZONE,
        venue TEXT,
        category TEXT,
        location TEXT,
        latitude FLOAT,
        longitude FLOAT,
        weather_condition TEXT,  -- 天气状况
        temperature INT,  -- 温度
        wind_speed TEXT,  -- 风速
        wind_direction TEXT  -- 风向
    );
    ''')
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    create_events_table()
