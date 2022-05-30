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


# Function which parses newly brought message into separate lines and info
def parse_message(info_string):
    # There are three main blocks: processes, system and windows
    message_list_windows, message_list_proc, message_list_integral = info_string.split("\nNEW_INFO\n")
    
    message_list_proc     = message_list_proc.split("\n")
    message_list_integral = message_list_integral.split("\n")
    message_list_windows  = message_list_windows.split("\n")
    processes = []

    # Parse for processes
    for line in message_list_proc:
        processes.append(tuple(line.split(",")))

    # Parse for system info
    integral_node = { 'proc_number': message_list_integral[0], 
                      'disk_mem_usege':  message_list_integral[1], 
                      'CPU_f_min': message_list_integral[2],
                      'CPU_f_max': message_list_integral[3], 
                      'CPU_f_cur': message_list_integral[4], 
                      'Boot_time': message_list_integral[5], 
                      'Total_mem_used': message_list_integral[6],  
                      'first_window': "None",
                      'first_window_percent': 0,
                      'second_window': "None",
                      'second_window_percent': 0,
                      'third_window': "None",
                      'third_window_percent': 0
                      }

    # Very primitive, but it works
    for line in message_list_windows:
        
        if 'Current window name::::' in line:
            integral_node['curent_window_active'] = line.split('::::')[1]
            continue

        if 'Maximum used window::::' in line:
            integral_node['first_window']         = line.split('::::')[1]
            integral_node['first_window_percent'] = line.split('::::')[2]
            continue

        if 'Second maximum used window::::' in line:
            integral_node['second_window']         = line.split('::::')[1]
            integral_node['second_window_percent'] = line.split('::::')[2]
            continue

        if 'Third maximum used window::::' in line:
            integral_node['third_window']         = line.split('::::')[1]
            integral_node['third_window_percent'] = line.split('::::')[2]
            continue

    return integral_node, processes


def AddUserInfoFromFile(nickname, computer, filename):
    info_string = ""
    file = open("n_" + filename, "r")
    info_string = file.read()
    file.close()
    os.remove("n_" + filename)

    # And parse all information
    node, processes = parse_message(info_string)
    try:
        DB_access.AddComputerInfo(DB_access.Session(), computer, node)

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
        await socket.register_user(data)
        AddUser(Session(), nickname, socket.machine_ids.index(machine_id) + 1, f"{host}:{port}")
    elif command == b"file" and identity in socket.clientdict:
        filename, filesize = unpackb(data)
        await socket.recv_file(data)
        AddUserInfoFromFile(socket.clientdict[identity][0], socket.machine_ids.index(socket.clientdict[identity][1]) + 1, filename)

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
    #try:
    serv = asyncio.run(Server.serve(DB_access.AddUser, AddUserInfoFromFile, DB_access.Session))
    #except:
        # Cleaning everything
    del Server
    print("[System]: Closing connection...")
    if bot:
        TGBot.kill()
        #if os.path.isfile("n_FileToSend.dat"):
            #os.remove("n_FileToSend.dat")


if __name__ == '__main__':
    main()