# -*- coding: utf-8 -*-
import numpy as np
import json 
try:
    from database.connection import get_db_connection
except ImportError:
    from connection import get_db_connection

class FacesRepository:

    @staticmethod
    def insert_person(name, embedding):
        """
        Insère une nouvelle personne dans la base
        name : prénom (unicode en Py2.7)
        embedding : numpy array (512,)
        """
        conn = get_db_connection()
        if conn is None:
            return

        try:
            cur = conn.cursor()
            embedding_json = json.dumps(embedding.tolist())

            cur.execute(
                "INSERT INTO persons (first_name, embedding) VALUES (%s, %s)",
                (name, embedding_json)
            )

            conn.commit()
            print(u"Enregistrement réussi pour {}".format(name))
        except Exception as e:
            print(u"Erreur insertion : " + str(e))
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_persons():
        """
        Récupère tous les visages connus
        """
        conn = get_db_connection()
        if conn is None:
            return []

        cur = conn.cursor()
        cur.execute("SELECT first_name, embedding FROM persons")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        result = []
        for name, embedding_data in rows:
            if embedding_data is None:
                continue

            try:
                embedding_list = json.loads(embedding_data)
                arr = np.array(embedding_list, dtype=float).flatten()

                if len(arr) != 512:
                    print(u"[WARN] Embedding pour {}: mauvaise taille {}, attendu 512".format(name, len(arr)))
                    continue

                result.append((name, arr))
            except Exception as e:
                print(u"Erreur décodage pour {}: {}".format(name, str(e)))

        return result