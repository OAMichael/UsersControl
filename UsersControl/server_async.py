#!/usr/bin/python3


import sys
import os
import signal
import traceback
import logging
import zmq
import asyncio
import zmq.asyncio
from aiofile import async_open
from msgpack import unpackb, packb


BUFSIZE = 2048
ENCODE = 'utf-8'
TCP_KEEPALIVE_TIMEOUT = 300
PIPELINE = 2

class TcpServer(object):

    def __init__(self, port, quantity_of_users, host = "0.0.0.0"):
        self.clientdict = {}
        self.connection_list = []
        self.machine_ids = []
        self.nicknames = []

        log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
        log_fname = os.path.join(log_dir, 'server_logfile.log')
        logging.basicConfig(filename=log_fname, filemode='w', encoding='utf-8', format='%(asctime)s %(message)s', level=logging.INFO)


        logging.info("Creating the server socket")
        self.ctx = zmq.asyncio.Context()
        self.server_socket = self.ctx.socket(zmq.ROUTER)
        
        try:
            self.server_socket.sndhwm = self.server_socket.rcvhwm = PIPELINE
        except AttributeError:
            logging.exception()
            self.server_socket.hwm = PIPELINE

        # Check and turn on TCP Keepalive
        x = self.server_socket.getsockopt(zmq.TCP_KEEPALIVE) 
        if (x == 0):
            logging.info("Socket Keepalive off, turning on")
            x = self.server_socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            logging.info('setsockopt ' + str(x))
            # Overrides value (in seconds) for keepalive
            self.server_socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, TCP_KEEPALIVE_TIMEOUT)
            self.server_socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, TCP_KEEPALIVE_TIMEOUT)
        else:
            logging.info("Socket Keepalive already on")


        # Assigning IP and port num to socket
        self.server_socket.bind(f"tcp://{host}:{port}")


        logging.info("Socket initializing completed!")

    def __del__(self):
        self.ctx.destroy()
        logging.info("Closing server")

    async def register_user(self, identity, data):
        nickname, machine_id, host, port = unpackb(data)
        if machine_id in self.machine_ids:
            await self.server_socket.send_multipart([
                identity,
                b"ID OCCUPIED",
            ])
            return False
        elif nickname in self.nicknames:
            await self.server_socket.send_multipart([
                identity,
                b"NICK OCCUPIED",
            ])
            return False
        else:
            self.clientdict[identity] = (nickname, machine_id, host, port)
            await self.server_socket.send_multipart([
                identity,
                b"OK",
            ])
            self.machine_ids.append(machine_id)
            self.nicknames.append(nickname)
            return True

    async def recv_file(self, identity, data):
        filename, filesize = unpackb(data)

        async with async_open('n_' + filename, 'wb') as file:

            credit = PIPELINE    # Up to PIPELINE chunks in transit

            total = 0            # Total bytes received
            chunks = b""         # Buffer for incoming file
            offset = 0           # Offset of next chunk request

            while True:
                while credit:
                    # ask for next chunk
                    await self.server_socket.send_multipart([
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
                        logging.exception()
                        raise 

                chunks += unpackb(chunk)

                credit += 1
                size = len(chunk)
                total += size
                if size < BUFSIZE:
                    break       # Last chunk received; exit


            await file.write(chunks)


    async def recv_and_process(self, AddUser, AddUserInfoFromFile, Session):
        msg = await self.server_socket.recv_multipart()
        if msg[1] == b"":
            return
        identity, command, data = msg
   
        if command == b"reg":
            nickname, machine_id, host, port = unpackb(data)
            if machine_id in self.machine_ids:
                await self.server_socket.send_multipart([
                    identity,
                    b"ID OCCUPIED",
                ])
            elif nickname in self.nicknames:
                await self.server_socket.send_multipart([
                    identity,
                    b"NICK OCCUPIED",
                ])
            else:
                self.clientdict[identity] = (nickname, machine_id, host, port)
                await self.server_socket.send_multipart([
                    identity,
                    b"OK",
                ])
                self.machine_ids.append(machine_id)
                self.nicknames.append(nickname)
                AddUser(Session(), nickname, self.machine_ids.index(machine_id) + 1, f"{host}:{port}")
        elif command == b"file" and identity in self.clientdict:
            filename, filesize = unpackb(data)

            async with async_open('n_' + filename, 'wb') as file:

                credit = PIPELINE    # Up to PIPELINE chunks in transit

                total = 0            # Total bytes received
                chunks = b""         # Buffer for incoming file
                offset = 0           # Offset of next chunk request

                while True:
                    while credit:
                        # ask for next chunk
                        await self.server_socket.send_multipart([
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
                            logging.exception()
                            raise 

                    chunks += unpackb(chunk)

                    credit += 1
                    size = len(chunk)
                    total += size
                    if size < BUFSIZE:
                        break       # Last chunk received; exit


                await file.write(chunks)

            AddUserInfoFromFile(self.clientdict[identity][0], self.machine_ids.index(self.clientdict[identity][1]) + 1, filename)            


    async def serve(self, AddUser, AddUserInfoFromFile, Session):
        poll = zmq.asyncio.Poller()
        poll.register(self.server_socket, zmq.POLLIN)
        poll.register(sys.stdin, zmq.POLLIN)

        while True:
            sockets = await poll.poll()
            sockets = dict(sockets)
            if sockets:
                if self.server_socket in sockets:
                    await self.recv_and_process(AddUser, AddUserInfoFromFile, Session)
                else:
                    st = sys.stdin.readline()
                    if "exit" in st:
                        raise KeyboardInterrupt


if __name__ == "__main__":
    host = str(input("Input server IP adress: "))
    port = int(input("Input server port: "))

    FileServer = TcpServer(port, host)

    asyncio.run(FileServer.serve())
    
    os.exit(0)












