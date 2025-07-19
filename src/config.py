import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_DBNAME = os.getenv("POSTGRESQL_DBNAME")


