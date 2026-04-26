# -*- coding: utf-8 -*-
import numpy as np
import json

from database.connection import get_db_connection


class FacesRepository:

    @staticmethod
    def insert_person(name, embedding):
        conn = get_db_connection()
        if conn is None:
            return None

        id_enfant = None
        try:
            cur = conn.cursor()

            cur.execute("INSERT INTO Enfants (prenom) VALUES (%s)", (name,))
            id_enfant = conn.insert_id()

            if embedding is not None:
                embedding_json = json.dumps(embedding.tolist())
                cur.execute(
                    "INSERT INTO Visages (id_enfant, encoding) VALUES (%s, %s)",
                    (id_enfant, embedding_json)
                )

            conn.commit()
            print(u"Enregistrement reussi pour {} (id={})".format(name, id_enfant))
            return id_enfant
        except Exception as e:
            print(u"Erreur insertion : " + str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_persons():
        conn = get_db_connection()
        if conn is None:
            return []

        persons = []
        try:
            cur = conn.cursor()
            sql = "SELECT e.prenom, v.encoding FROM Enfants e JOIN Visages v ON e.id = v.id_enfant"
            cur.execute(sql)
            results = cur.fetchall()

            for row in results:
                name = row[0]
                embedding = np.array(json.loads(row[1]))
                persons.append((name, embedding))

            return persons
        except Exception as e:
            print("Erreur lecture DB : " + str(e))
            return []
        finally:
            cur.close()
            conn.close()
