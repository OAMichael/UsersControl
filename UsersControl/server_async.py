#!/usr/bin/python3


import sys
import signal
import traceback
import zmq
import asyncio
import zmq.asyncio
from aiofile import async_open
from msgpack import unpackb, packb




BUFSIZE = 2048
ENCODE = 'utf-8'
TCP_KEEPALIVE_TIMEOUT = 300
PIPELINE = 10

class TcpServer(object):

    def __init__(self, port, quantity_of_users, host = "0.0.0.0"):
        self.clients = 0
        self.clientdict = {}
        self.nicknamesdict = {}
        self.connection_list = []

        print ("* Creating the server socket")
        self.ctx = zmq.asyncio.Context()
        self.server_socket = self.ctx.socket(zmq.ROUTER)
        
        socket_set_hwm(self.server_socket, PIPELINE) 

        # Check and turn on TCP Keepalive
        x = self.server_socket.getsockopt(zmq.TCP_KEEPALIVE) 
        if (x == 0):
            print ("* Socket Keepalive off, turning on")
            x = self.server_socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            print ('* setsockopt ' + str(x))
            # Overrides value (in seconds) for keepalive
            self.server_socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, TCP_KEEPALIVE_TIMEOUT)
        else:
            print ("* Socket Keepalive already on")


        # Assigning IP and port num to socket
        self.server_socket.bind(f"tcp://{host}:{port}")


        signal.signal(signal.SIGINT, self.sighandler)
        print("* Socket initializing completed!")

    def __del__(self):
        self.ctx.destroy()


    def sighandler(self, signum, frame):

        print("* Closing server...")
        sys.exit(1)

    async def recv_and_process(self):
        msg = await self.server_socket.recv_multipart()
        if msg[1] == b"":
            return
        identity, command, data = msg

        if (command == b"msg"):
            print(data.decode(ENCODE))
        elif (command == b"reg"):
            nickname, host, port = unpackb(data)
            if (nickname in self.clientdict):
                await self.server_socket.send_multipart([
                    identity,
                    b"OCCUPIED",
                ])
            else:
                self.clientdict[nickname] = {identity, host, port}
                await self.server_socket.send_multipart([
                    identity,
                    b"OK",
                ])
        elif (command == b"file" ):
            filename, filesize = unpackb(data)

            print("[Server]: receiving...")
            async with async_open('n_' + filename, 'wb') as file:

                credit = PIPELINE    # Up to PIPELINE chunks in transit

                total = 0            # Total bytes received
                chunks = b""         # Buffer for incoming file
                offset = 0           # Offset of next chunk request

                while True:
                    while credit:
                        # ask for next chunk
                        self.server_socket.send_multipart([
                            identity,
                            b"fetch",
                            b"%i" % offset,
                            b"%i" % BUFSIZE,
                        ])

                        offset += BUFSIZE
                        credit -= 1
                    try:
                        msg = await self.server_socket.recv_multipart()
                        identity, chunk = msg
                    except zmq.ZMQError as exc:
                        if e.errno == zmq.ETERM:
                            return # shutting down, quit
                        else:
                            raise 

                    chunks += unpackb(chunk)

                    credit += 1
                    size = len(chunk)
                    total += size
                    if size < BUFSIZE:
                        break       # Last chunk received; exit


                await file.write(chunks)
                print("[Server]: done writing!")


    async def serve(self):
        poll = zmq.asyncio.Poller()
        poll.register(self.server_socket, zmq.POLLIN)
        poll.register(sys.stdin, zmq.POLLIN)

        while True:
            sockets = await poll.poll()
            sockets = dict(sockets)
            if sockets:
                if self.server_socket in sockets:
                    await self.recv_and_process()
                else:
                    st = input()
                    if (st == "/list"):
                        for keys, values in self.clientdict.items():
                            values = list(values)
                            print(f"{keys}: {values[0]} | {values[1]} | {values[2]}")
                    else:
                        print(f"Entered message: {st}")


def socket_set_hwm(socket, hwm=-1):
    try:
        socket.sndhwm = socket.rcvhwm = hwm
    except AttributeError:
        socket.hwm = hwm


if __name__ == "__main__":
    host = str(input("Input server IP adress: "))
    port = int(input("Input server port: "))

    FileServer = TcpServer(port, host)

    asyncio.run(FileServer.serve())
    
    os.exit(0)












