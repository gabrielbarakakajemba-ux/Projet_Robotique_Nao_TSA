# -*- coding: utf-8 -*-
import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, root_path)

from flask import Flask, request, jsonify
from ollama import chat
from collections import deque
from datetime import datetime

app = Flask(__name__)

SYSTEM_PROMPT = """Tu es Nao, un robot assistant therapeutique et educatif pour enfants autistes.
- Reponds toujours en francais de maniere tres calme et rassurante.
- Fais des phrases tres courtes, simples et litterales (1 phrase maximum, sans sarcasme ni figures de style complexes).
- Utilise des mots concrets et previsibles.
- Si l'enfant exprime une emotion, valide la et propose une petite routine (ex: 'Je vois que tu es triste, on peut respirer ensemble.').
- Si le message commence par [L'utilisateur s'appelle X], utilise son prenom de facon douce : 'Bonjour X'.
- Si tu ne comprends pas ou que l'enfant ne parle pas, dis simplement : 'Je suis la avec toi.'
- Aucun format de texte, que des mots simples a prononcer, pas d'emojis.
- Rappelle-toi : l'objectif est d'apaiser l'enfant, de l'accompagner dans les routines et d'encourager la communication simple sans le brusquer."""

conversation_history = deque(maxlen=10)


def log(tag, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print("[{}][{}] {}".format(timestamp, tag, message))


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    log("SERVER", "Requete recue")

    try:
        data = request.json
        user_message = data.get("message")
        log("SERVER", "Message utilisateur : {}".format(user_message))

        if not user_message:
            log("SERVER", "ERREUR - Message vide")
            return jsonify({"error": "No message provided"}), 400

        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        log("SERVER", "Historique : {}/{} messages".format(len(conversation_history), conversation_history.maxlen))

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(conversation_history)
        log("SERVER", "Appel LLM avec {} messages (system inclus)".format(len(messages)))

        response = chat(
            model="mistral-large-3:675b-cloud",
            messages=messages,
            options={
                "temperature": 0.75,
                "top_p": 0.9,
                "num_predict": 80,
            }
        )

        assistant_reply = response["message"]["content"]
        log("SERVER", "Reponse LLM : {}".format(assistant_reply))

        conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        log("SERVER", "Envoi de la reponse au client")
        return jsonify({"response": assistant_reply})

    except Exception as e:
        log("SERVER", "ERREUR - {}".format(str(e)))
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    conversation_history.clear()
    log("SERVER", "Memoire de conversation effacee")
    return jsonify({"status": "Memoire effacee"})


@app.route("/history", methods=["GET"])
def history():
    log("SERVER", "Consultation de l'historique")
    return jsonify({"history": list(conversation_history)})


if __name__ == "__main__":
    log("SERVER", "Demarrage du serveur LLM sur port 5000...")
    app.run(host="0.0.0.0", port=5000)
