#!/usr/bin/python3

import sys
import traceback
import zmq
import os
from msgpack import unpackb, packb

BUFSIZE = 2048
ENCODE = 'utf-8'
SOCKET_TIMEOUT = 10
TCP_KEEPALIVE_TIMEOUT = 300
PIPELINE = 10

class TcpClient(object):

    def __init__(self, host, port, nickname):
        print ("* Creating the server socket")
        self.ctx = zmq.Context()
        self.client_socket = self.ctx.socket(zmq.DEALER)
        
        socket_set_hwm(self.client_socket, PIPELINE)

        # Check and turn on TCP Keepalive
        x = self.client_socket.getsockopt(zmq.TCP_KEEPALIVE) 
        if (x == 0):
            print ("* Socket Keepalive off, turning on")
            x = self.client_socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            print ('* setsockopt ' + str(x))
            # Overrides value (in seconds) for keepalive
            self.client_socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, TCP_KEEPALIVE_TIMEOUT)
        else:
            print ("* Socket Keepalive already on")
        
        # Assigning IP and port num to socket
        self.client_socket.connect(f"tcp://{host}:{port}")

        print("* Socket initializing completed!")

        while True:
            self.client_socket.send_multipart([
                b"reg",
                packb([nickname, host, port]),
            ])

            msg = self.client_socket.recv()
            if (msg ==b"OK"):
                break
            elif (msg == b"OCCUPIED"):
                input_string = input("Your nickname is occupied! Enter another one, or command <exit> to end program:")
                if (input_string == "exit"):
                    sys.exit(0)
                else:
                    nickname = input_string
                    continue
            else:
                raise RuntimeError("Unknown server reply")

        print("* Connection successfully registered!")

            
    def register_nickname(self, nickname):
        self.client_socket.sendall(f"$nick_{nickname}$")

    def sendfile(self, filepath, file):
        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        self.client_socket.send_multipart([
            b"file", 
            packb([filename, filesize]),
        ])

        while True:

            try:
                msg = self.client_socket.recv_multipart()
            except zmq.ZMQError as exc:
                if exc.errno == zmq.ETERM:
                    return    # shutting down, quit
                else:
                    raise

            command, offset_str, chunksz_str = msg

            offset = int(offset_str)
            chunksz = int(chunksz_str)

            # Read chunk of data from file
            file.seek(offset, os.SEEK_SET)
            data = file.read(chunksz)

            if not data:
                print("Sending complete!")
                break

            #data = packb(data)

            self.client_socket.send(packb(data))

            
    def sendmsg(self, msg):
            self.client_socket.send_multipart([
                b"msg",
                msg.encode(ENCODE),
            ])

def socket_set_hwm(socket, hwm=-1):
    try:
        socket.sndhwm = socket.rcvhwm = hwm
    except AttributeError:
        socket.hwm = hwm


if __name__ == "__main__":
    host = str(input("Input client IP adress: "))
    port = int(input("Input client port: "))
    nickname = str(input("Input nickname: "))

    FileClient = TcpClient(host, port, nickname)

    filepath = "./dir/cloud.jpg"
    file = open(filepath, "rb")

    FileClient.sendfile(filepath, file)

    file.close()




