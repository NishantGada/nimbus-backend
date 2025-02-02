import mysql.connector
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("host"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "database": os.getenv("database")
}

# Connect to Database
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)