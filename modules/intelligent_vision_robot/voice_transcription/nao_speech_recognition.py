# -*- coding: utf-8 -*-
import paramiko
import speech_recognition as sr
from naoqi import ALProxy
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from config.nao_config import ROBOT_IP, PORT, NAO_AUDIO_FILE, LOCAL_AUDIO_FILE, NAO_PASSWORD, NAO_USERNAME

def stop_recording():
    audio_recorder = ALProxy("ALAudioRecorder", ROBOT_IP, PORT)
    audio_recorder.stopMicrophonesRecording()
    
# Fonction pour écouter les réponses des utilisateurs
def record_audio(start_manual=False):
    audio_recorder = ALProxy("ALAudioRecorder", ROBOT_IP, PORT)
    try:
        audio_recorder.stopMicrophonesRecording()
    except RuntimeError:
        pass
    audio_recorder.startMicrophonesRecording(NAO_AUDIO_FILE, "wav", 16000, (0,0,1,0))
    if not start_manual:
        time.sleep(5)
        audio_recorder.stopMicrophonesRecording()

#Fonction pour transférer le fichier audio localement
def transfer_audio_file():
    print("Transfert du fichier de Nao à la machine local...")

    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ROBOT_IP, username=NAO_USERNAME, password=NAO_PASSWORD)

    scp=paramiko.SFTPClient.from_transport(ssh.get_transport())
    scp.get(NAO_AUDIO_FILE, LOCAL_AUDIO_FILE)
    scp.close()
    print("Transfert complété")

# Fonction pour convertir l'audio en texte
def speech_to_text():
    recognizer = sr.Recognizer()

    # Charger le fichier audio enregistré par Nao
    with sr.AudioFile(LOCAL_AUDIO_FILE) as source:
        print("Analyse de l'audio...")
        recognizer.adjust_for_ambient_noise(source)  # Ajuste au bruit
        try:
            audio = recognizer.record(source)  # Récupère tout l'audio
            text = recognizer.recognize_google(audio, language="fr-FR", show_all=False)  # Détection en français et on évite d'affiche les transcriptions de speech_recognition
            print("Tu as dit : " + text)
            return text
        except sr.UnknownValueError:
            print("Nao n'a pas compris.")
            return None
        except sr.RequestError:
            print("Erreur de connexion à Google Speech Recognition.")
            return None
 