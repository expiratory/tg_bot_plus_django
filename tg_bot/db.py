from os import getenv
from dotenv import load_dotenv, find_dotenv
import psycopg2


load_dotenv(find_dotenv())


async def connect_to_db():
    conn = psycopg2.connect(
        dbname=getenv('POSTGRES_DB'),
        user=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=getenv('POSTGRES_HOST')
    )
    cursor = conn.cursor()
    return cursor, conn


async def close_db(cursor, conn):
    cursor.close()
    conn.close()
