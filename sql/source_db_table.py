import mysql.connector
import pandas as pd, random, names, string, time
import datetime, os, sys
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).parent.absolute()
# print(root_dir)
# sys.exit()
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# conn = mysql.connector.connect(
#     host='host.docker.internal',
#     port=3305,
#     user='root',
#     password=os.getenv('SOURCE_DB_ROOT_PASSWORD'),
#     db=
# )

# print(conn)

# cursor = conn.cursor()
# cursor.execute('CREATE DATABASE IF NOT EXISTS sourcedb CHARACTER SET utf8 COLLATE utf8_general_ci;')
# cursor.close() 
# sys.exit()

db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('SOURCE_DB_PORT'),
    user='root',
    password=os.getenv('SOURCE_DB_ROOT_PASSWORD'),
    database=os.getenv('SOURCE_DB_DATABASE')
)

cursor = db.cursor()

with open('sourcedb.sql') as f:
    cursor.execute(f.read(), multi=True)

time.sleep(5)
cursor.close()
db.close()