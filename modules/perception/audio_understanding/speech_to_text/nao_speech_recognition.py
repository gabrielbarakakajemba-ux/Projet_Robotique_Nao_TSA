# -*- coding: utf-8 -*-
import paramiko
import speech_recognition as sr
import time
import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

if root not in sys.path:
    sys.path.insert(0, root)

try:
    from config.python_paths import NAOQI_LIB_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
except ImportError:
    sys.path.insert(0, "/home/mr-kajemba/Nao_Autisme")
    from config.python_paths import NAOQI_LIB_PATH
    sys.path.insert(0, NAOQI_LIB_PATH)

from naoqi import ALProxy
import speech_recognition as sr

from config.nao_config import ROBOT_IP, PORT, NAO_AUDIO_FILE, LOCAL_AUDIO_FILE, NAO_PASSWORD, NAO_USERNAME
from cryptography.hazmat.backends import default_backend

def stop_recording():
    audio_recorder = ALProxy("ALAudioRecorder", ROBOT_IP, PORT)
    audio_recorder.stopMicrophonesRecording()

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

def transfer_audio_file():
    print("Transfert du fichier de Nao a la machine locale...")

    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ROBOT_IP, username=NAO_USERNAME, password=NAO_PASSWORD)

    scp=paramiko.SFTPClient.from_transport(ssh.get_transport())
    scp.get(NAO_AUDIO_FILE, LOCAL_AUDIO_FILE)
    scp.close()
    print("Transfert complete")

def speech_to_text():
    recognizer = sr.Recognizer()

    with sr.AudioFile(LOCAL_AUDIO_FILE) as source:
        print("Analyse de l'audio...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="fr-FR", show_all=False)
            print("Tu as dit : " + text)
            return text
        except sr.UnknownValueError:
            print("Nao n'a pas compris.")
            return None
        except sr.RequestError:
            print("Erreur de connexion a Google Speech Recognition.")
            return None
