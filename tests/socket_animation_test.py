# -*- coding: utf-8 -*-
import socket
import struct

def test_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5005)) # Port de test
    server.listen(1)
    print("En attente du NAO sur le port 5005...")
    
    conn, addr = server.accept()
    print("Connexion etablie avec le NAO !")
    
    # Test d'envoi de texte
    msg = "HELLO_TEST"
    payload = msg.encode('utf-8')
    conn.sendall(struct.pack(">L", len(payload)) + payload)
    conn.close()

if __name__ == "__main__":
    test_server()