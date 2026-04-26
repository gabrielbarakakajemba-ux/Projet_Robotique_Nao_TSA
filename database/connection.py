# -*- coding: utf-8 -*-
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="P_Robot_Nao",
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print("Erreur de connexion : " + str(e))
        return None

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Connexion reussie sous Python 2.7 !")
        conn.close()
