from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv(dotenv_path="config/.env")
user = os.getenv("MYSQL_USER")
print("Current MySQL user:", user)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return None

def save_conversation(db, user_input, response):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_input, assistant_response) VALUES (%s, %s)",
        (user_input, response)
    )
    db.commit()

def save_task(db, task):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (task,))
    db.commit()
