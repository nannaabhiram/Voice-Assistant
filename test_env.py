from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config/.env")  # Make sure the path is correct

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
db = os.getenv("MYSQL_DB")

print("Host:", host)
print("User:", user)
print("Password:", password)
print("DB Name:", db)
