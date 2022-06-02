import psycopg2, time, os
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

db = psycopg2.connect(
  host=os.getenv('DB_HOST'),
  port=os.getenv('TARGET_DB_PORT'),
  user=os.getenv('TARGET_DB_USER'),
  password=os.getenv('TARGET_DB_PASSWORD'),
  database=os.getenv('TARGET_DB_NAME')
)

cursor = db.cursor()

with open('targetdb.sql') as f:
  cursor.execute(f.read(), multi=True)
time.sleep(5)
cursor.close()
db.close()