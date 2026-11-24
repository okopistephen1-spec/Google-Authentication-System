import sqlite3

from database import get_db_connection


def promote_to_admin(email):

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE users
            SET role = 'admin'
            WHERE email = ?
        """, (email,))

        if cursor.rowcount == 0:
            print("No user found with that email address.")

        else:
            connection.commit()
            print(f"{email} is now an administrator.")

    finally:
        connection.close()


if __name__ == "__main__":

    email = input("Enter the user's registered email: ").strip()

    if email:
        promote_to_admin(email)

    else:
        print("Email address cannot be empty.")