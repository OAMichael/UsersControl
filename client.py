#!/usr/bin/python3

import socket
import sys
import select
import os
import traceback

BUFSIZE = 2048
ENCODE = 'utf-8'
SOCKET_TIMEOUT = 2

class TcpClient(object):

    def __init__(self, host, port):
        # AF_INET - internet socket, SOCK_STREAM - connection-based protocol for TCP, 
        # IPPROTO_TCP - choosing TCP
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            self.client_socket.settimeout(SOCKET_TIMEOUT)
            self.client_socket.connect((host, port))
            print("* Connected to server")

        except socket.error:
            print("* Could not connect to server")

        # Check and turn on TCP Keepalive
        try:
            x = self.client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
            if (x == 0):
                x = self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # Overrides value (in seconds) for keepalive
                self.client_socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 300)
            print("* Tcp keepalive now is on")
        except:
            print("* Error processing TCP Keepalive!")
            traceback.print_exc()
            sys.exit(1)  

    def sendmsg(self, msg):
        try:
            self.client_socket.sendall(msg.encode(ENCODE))
        except Exception as exc:
            raise exc

    def sendfile(self, filepath, file):
        filesize = os.path.getsize(filepath)
        filename = filepath.split('/')[-1]
        self.client_socket.send(f"${filename}_{filesize}$".encode(ENCODE))
        answer = self.client_socket.recv(BUFSIZE).decode(ENCODE)
        if (answer == "$filenamereceived$"):
            data = file.read()
            totalsent = 0
            while totalsent < filesize:
                sent = self.client_socket.send(data[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent 

            #if (totalsent == filesize):
                #print("[Client]: done sending. Waiting for confirmation...")

        else:
            raise RuntimeError("File sending failed")

        answer = self.client_socket.recv(BUFSIZE).decode(ENCODE)
        if (answer == "$filerecieved$"):
            print("[Client]: confirmation received!")
        else:
            print("Unknown message instead of confirmation")


if __name__ == "__main__":
    host = str(input("Input client IP adress: "))
    port = int(input("Input client port: "))

    FileClient = TcpClient(host, port)

    filepath = "./dir/example.txt"
    file = open(filepath, "rb")

    FileClient.sendfile(filepath, file)




