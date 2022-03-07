# Yonatan Cohen, 324842608

import random
import socket
import sys
import threading

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

messages = []  # messages gathered last 60 seconds
mutex = threading.Lock()


def main():
    server_port = int(open("ips.txt", "r").readlines()[int(sys.argv[1]) - 1].split()[1])

    # receive messages:
    t1 = threading.Thread(target=receiving_thread, args=(server_port,))
    t1.start()

    # send messages:
    t2 = threading.Timer(60.0, sending_thread)
    t2.start()


def receiving_thread(server_port):
    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', server_port))  # server listens to all IP's

    # put the socket into listening mode
    s.listen()

    # a forever loop to receive clients
    while True:
        conn, addr = s.accept()
        threading.Thread(target=receive_message, args=(conn,)).start()  # creating a new thread


def receive_message(conn):
    # receive message
    data = conn.recv(8192)  # pk3 is 8192 bytes, needs to be changed if we have bigger keys
    conn.close()
    global messages

    # load secret key
    with open("sk{}.pem".format(sys.argv[1]), 'rb') as f:
        sk = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    li = sk_decrypt(sk, data)  # decrypt message
    dest_ip, dest_port = decode_ip_and_port(li[0:4], li[4:6])  # extract ip & port
    mutex.acquire()  # block access to messages
    messages.append([dest_ip, dest_port, li[6:]])  # add message to messages
    mutex.release()  # unblock access to messages


def sending_thread():
    threading.Timer(60.0, sending_thread).start()  # create a thread to send all messages in next 60 secs
    global messages
    mutex.acquire()  # block access to messages
    last_minute_messages = messages  # save messages from last minute
    messages = []  # empty the list
    mutex.release()  # unblock access to messages
    random.shuffle(last_minute_messages)  # randomly shuffle messages
    for message in last_minute_messages:
        threading.Thread(target=send_message, args=(message,)).start()


def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    s.connect((message[0], message[1]))
    s.send(message[2])  # send message
    s.close()  # close socket


def sk_decrypt(secret_key, ciphertext):
    return secret_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decode_ip_and_port(ip, port):
    ip = "{}.{}.{}.{}".format(ip[0], ip[1], ip[2], ip[3])
    port = int.from_bytes(port, "big")
    return ip, port


if __name__ == '__main__':
    main()
