#!/usr/bin/env python3

import struct
import socket
import pickle
import sys
from time import sleep

from gnssr.tds.detection.find_targets import *

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def main():
    processor = target_processor()

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    message = input(" -> ")

    while message != 'quit':

        if message == "START":
            while True:
                soc.sendall("GET_TM".encode("utf8"))
                res = soc.recv(5120).decode("utf8")
                if res == 'NEW_DATA':
                    data = recv_msg(soc)
                    telemetry = pickle.loads(data)
                    for line in telemetry:
                        print(line)
                elif res == 'NO_NEW_DATA':
                    pass
                sleep(0.5)

        else:
            soc.sendall(message.encode("utf8"))
            res = soc.recv(5120).decode("utf8")
            if res == "-":
                pass        # null operation

        message = input(" -> ")

    soc.send(b'--QUIT--')

if __name__ == "__main__":
    main()
