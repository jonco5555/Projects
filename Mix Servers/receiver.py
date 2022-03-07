# Yonatan Cohen, 324842608

import base64
import datetime
import socket
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def main():
    port = int(sys.argv[3])
    key = generate_key(sys.argv[1], sys.argv[2])  # generate symmetric key by the arguments

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))  # server listens to all IP's

    # put the socket into listening mode
    s.listen()

    # a forever loop to receive clients
    while True:
        conn, addr = s.accept()
        # receive message
        data = conn.recv(8192)  # pk3 is 8192 bytes
        conn.close()

        plaintext = key.decrypt(data).decode()  # decrypt message
        print("{} {}".format(plaintext, datetime.datetime.now().strftime("%H:%M:%S")))


def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    return Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))


if __name__ == '__main__':
    main()
