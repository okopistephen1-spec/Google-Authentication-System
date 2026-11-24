import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, "users.db")


def get_db_connection():
    connection = sqlite3.connect("DATABASE_PATH")
    return connection


def create_users_table():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            google_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            profile_picture TEXT,

            role TEXT NOT NULL DEFAULT 'member',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Check whether the role column already exists
    cursor = connection.execute("PRAGMA table_info(users)")

    columns = [column[1] for column in cursor.fetchall()]

    # Add the role column if this is an existing database
    if "role" not in columns:

        connection.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT NOT NULL DEFAULT 'member'
        """)

    connection.commit()
    connection.close()


if __name__ == "__main__":

    create_users_table()

    print("Users table has been created successfully!")