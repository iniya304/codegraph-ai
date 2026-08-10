import os
import sqlite3


def login(username, password):
    # Intentional SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def divide(a, b):
    # Intentional ZeroDivisionError risk
    return a / b


def delete_file(filename):
    # Intentional Command Injection vulnerability
    os.system("rm " + filename)