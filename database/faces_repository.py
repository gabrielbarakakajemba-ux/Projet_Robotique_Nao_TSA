# -*- coding: utf-8 -*-
import numpy as np
import json 

from database.connection import get_db_connection


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

            cur.execute("INSERT INTO Enfants (prenom) VALUES (%s)", (name,))
            id_enfant = conn.insert_id()

            # 2. Insertion du visage
            embedding_json = json.dumps(embedding.tolist())
            # Ici il y a DEUX %s car on envoie DEUX données : id_enfant et embedding_json
            cur.execute(
                "INSERT INTO Visages (id_enfant, encoding) VALUES (%s, %s)", 
                (id_enfant, embedding_json)
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
        Récupère tous les visages enregistrés pour la reconnaissance.
        """
        conn = get_db_connection()
        if conn is None:
            return []

        persons = []
        try:
            cur = conn.cursor()
            # On joint les tables pour avoir le nom et l'encodage
            sql = "SELECT e.prenom, v.encoding FROM Enfants e JOIN Visages v ON e.id = v.id_enfant"
            cur.execute(sql)
            results = cur.fetchall()

            for row in results:
                name = row[0]
                # On retransforme le texte JSON en liste Python, puis en array Numpy
                embedding = np.array(json.loads(row[1]))
                persons.append((name, embedding))
                
            return persons
        except Exception as e:
            print("Erreur lecture DB : " + str(e))
            return []
        finally:
            cur.close()
            conn.close()