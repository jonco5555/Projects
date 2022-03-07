# Yonatan Cohen, 324842608

import sys
import socket
import threading
import base64
import time

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

messages = []  # messages[i] = list of messages should be sent in round i
mutex = threading.Lock()


def main():
    with open("messages{}.txt".format(sys.argv[1]), "r") as msgs_x:  # read messages file
        lines = [line.rstrip('\n') for line in msgs_x]
    sorted_lines = sorted(lines, key=lambda row: int(row.split()[-5]))  # sort the lines by its' round

    # create empty list for encrypted messages
    max_rnd = int(sorted_lines[len(sorted_lines) - 1].split()[-5])
    global messages
    for i in range(max_rnd + 1):
        messages.append([])  # initialize messages

    # read and save ips for later
    ips_file = open("ips.txt", "r")
    ips = []
    for line in ips_file:
        ips.append(line.strip('\n'))

    # create a thread to send messages
    threading.Thread(target=sending_thread, args=(0,)).start()

    for line in sorted_lines:
        # extract parameters
        line = line.split()
        message = line[0:len(line) - 6]
        message = ' '.join(message)  # to handle spaces
        path, rnd, password, salt, dest_ip, dest_port = line[-6:]

        key = generate_key(password, salt)  # generate symmetric key by the parameters

        # encrypting process
        counter = 0
        j = 0
        l_i = ''
        path = path.split(',')
        path.reverse()
        for i in path:  # "onion"
            if counter == 0:
                c = key.encrypt(message.encode())
                enc_ip, enc_port = encode_ip_and_port(dest_ip, dest_port)
            else:
                c = l_i
                enc_ip, enc_port = encode_ip_and_port(ips[j].split()[0], ips[j].split()[1])
            msg = enc_ip + enc_port + c
            with open("pk{}.pem".format(i), 'rb') as f:
                pk_i = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            l_i = pk_encrypt(pk_i, msg)
            j = int(i) - 1
            counter += 1

        # add to messages
        mutex.acquire()
        messages[int(rnd)].append([ips[j].split()[0], ips[j].split()[1], l_i])
        mutex.release()


def sending_thread(i):
    global messages
    # while last round was not arrived create a thread to send next round' messages in 60 seconds from now
    if i < len(messages) - 1:
        threading.Timer(60.0, sending_thread, args=(i + 1,)).start()
    time.sleep(2)  # sleep 2 seconds before sending

    while True:
        if messages[i]:  # if there is a message ready to sent
            mutex.acquire()
            message = messages[i].pop(0)  # remove the message
            mutex.release()
            threading.Thread(target=send_message, args=(message,)).start()  # create a thread to send it


def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    s.connect((message[0], int(message[1])))
    s.send(message[2])  # send message
    s.close()  # close socket


def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    return Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))


def encode_ip_and_port(ip, port):
    ip = ip.split('.')
    for i in range(4):
        ip[i] = int(ip[i])
    ip = bytes(ip)
    port = int(port).to_bytes(2, "big")
    return ip, port


def pk_encrypt(public_key, message):
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


if __name__ == '__main__':
    main()
