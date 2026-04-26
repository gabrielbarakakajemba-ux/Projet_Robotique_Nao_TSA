# -*- coding: utf-8 -*-
import json

try:
    from database.connection import get_db_connection
except ImportError:
    from connection import get_db_connection


class DefisRepository:

    @staticmethod
    def get_by_type(type_jeu, limit=5):
        conn = get_db_connection()
        if conn is None:
            return []

        defis = []
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, consigne, animation, reponse, synonymes, indice, niveau "
                "FROM Defis_Jeu WHERE type_jeu=%s ORDER BY niveau ASC, RAND() LIMIT %s",
                (type_jeu, int(limit))
            )
            rows = cur.fetchall()

            for row in rows:
                synonymes = []
                if row[4]:
                    try:
                        synonymes = json.loads(row[4])
                    except Exception:
                        synonymes = []
                defis.append({
                    'id'        : row[0],
                    'consigne'  : row[1],
                    'animation' : row[2],
                    'reponse'   : row[3],
                    'synonymes' : synonymes,
                    'indice'    : row[5],
                    'niveau'    : row[6],
                })
            return defis
        except Exception as e:
            print("Erreur lecture Defis_Jeu : " + str(e))
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def log_session(id_session, nom_jeu, score, observations=""):
        conn = get_db_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Jeux_Interactifs (id_session, nom_jeu, score, observations) "
                "VALUES (%s, %s, %s, %s)",
                (id_session, nom_jeu, score, observations)
            )
            conn.commit()
        except Exception as e:
            print("Erreur log session : " + str(e))
        finally:
            cur.close()
            conn.close()
