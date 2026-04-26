# -*- coding: utf-8 -*-
try:
    from database.connection import get_db_connection
except ImportError:
    from connection import get_db_connection

class QuestionRepository:

    @staticmethod
    def get_all_questions():
        conn = get_db_connection()
        if conn is None: return []

        cur = conn.cursor()
        cur.execute("SELECT id, question, answer FROM questions_list")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def add_question(question, answer):
        conn = get_db_connection()
        if conn is None: return

        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO questions_list (question, answer) VALUES (%s, %s)",
                (question, answer)
            )
            conn.commit()
        except Exception as e:
            print(u"Erreur lors de l'ajout de la question : " + str(e))
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_answers():
        conn = get_db_connection()
        if conn is None: return []

        cur = conn.cursor()
        cur.execute("SELECT answer FROM questions_list")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [row[0] for row in rows]
