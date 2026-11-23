import sqlite3

def get_db_connection():
    connection = sqlite3.connect("users.db")

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

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":
    create_users_table()

    print("Users table has been created successfully!")