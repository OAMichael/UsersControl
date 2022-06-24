#!/usr/bin/python3

import socket
import select
import traceback
import sys
import subprocess
import time
import asyncio
from datetime import datetime
from collections import deque
from server_async import TcpServer
import os
from models.Database import DATABASE_NAME
from models.Database import Session
import CreateDB
import DB_access
import zmq
from msgpack import unpackb, packb


def AddUserInfo(nickname, computer, machine_id, data):

    # And parse all information
    integral_node, processes = data
    try:
        DB_access.AddComputerInfo(DB_access.Session(), machine_id, computer, integral_node)

        for process in processes:
            proc_node = {   'app_name': process[0],
                            'computer': computer,
                            'create_time': process[1],
                            'status': process[2],
                            'rss': process[3],
                            'vms': process[4],
                            'shared': process[5],
                            'data': process[6]
                       }
            DB_access.AddApplication(DB_access.Session(), proc_node)
    except:
        pass


async def recv_and_process_loop(socket):
    msg = await socket.server_socket.recv_multipart()
    if msg[1] == b"":
        return
    identity, command, data = msg

    if command == b"reg":
        nickname, machine_id, host, port = unpackb(data)
        adding = await socket.register_user(identity, data)
        if adding:
            DB_access.AddUser(Session(), nickname, machine_id, socket.machine_ids.index(machine_id) + 1, f"{host}:{port}")

    elif command == b"msgpack" and identity in socket.clientdict:
        new_data = unpackb(data)
        AddUserInfo(socket.clientdict[identity][0], 
                    socket.machine_ids.index(socket.clientdict[identity][1]) + 1,
                    socket.clientdict[identity][1],
                    new_data)


async def serve_loop(socket):
    poll = zmq.asyncio.Poller()
    poll.register(socket.server_socket, zmq.POLLIN)
    poll.register(sys.stdin, zmq.POLLIN)

    while True:
        sockets = await poll.poll()
        sockets = dict(sockets)
        if sockets:
            if socket.server_socket in sockets:
                await recv_and_process_loop(socket)
            else:
                st = sys.stdin.readline()
                if "exit" in st:
                    raise KeyboardInterrupt

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [config_path]")
        sys.exit(1)
    # First of all, configurate the server

    # sys.argv[1] - it's config path
    with open(sys.argv[1], "r") as file:
        host = file.readline().strip("\n").split("host = ")[1]
        port = int(file.readline().strip("\n").split("port = ")[1])
        num_of_workers = int(file.readline().strip("\n").split("num_of_workers = ")[1])
        bot = ("True" in file.readline())
        if bot:
            bot_cfg_path = file.readline().strip("\n").split("bot_cfg_path = ")[1]


    Server = TcpServer(port, host)
    print("[System]: Socket setup has been done!")

    db_existed = os.path.exists(DATABASE_NAME)
    if not db_existed:
        CreateDB.create_database(False)
        print("[System]: Database has been created!")
    else:
        print("[System]: Database has been connected!")

    # Does not wait, but we don't need to, because kill it while closing connection
    if bot:
        global TGBot
        TGBot = subprocess.Popen(["./TGBot.py", f"{bot_cfg_path}"])
        print("[System]: Telegram bot has been activated!")

    # Main loop
    try:
        serv = asyncio.run(serve_loop(Server))
    except KeyboardInterrupt:
        # Cleaning everything
        del Server
        print("[System]: Closing connection...")
        if bot:
            TGBot.kill()


if __name__ == '__main__':
    main()