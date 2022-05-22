#!/usr/bin/python3

import socket
import select
import traceback
import sys
import subprocess
import time
from datetime import datetime
from collections import deque
from server import TcpServer
import os
from models.Database import DATABASE_NAME
from models.Database import Session
import CreateDB
import DB_access

# Connection Data
BUFSIZE = 2048
ENCODE = 'utf-8'
TCP_KEEPALIVE_TIMEOUT = 300

# Lists for program work
connection_list = []
nicknames = []
addresses = []

# Command which persuade server to close connection
quit_list = ["quit\n", "Quit\n", "q\n", "exit\n", "Exit\n"]


# Function to disconnect particular user
def disconnect_client(user):
    if user in connection_list:
        index = connection_list.index(user)
        connection_list.remove(user)
        del nicknames[index]
        del addresses[index]
        try:
            user.shutdown(socket.SHUT_RDWR)
            user.close()
        except Exception as e:
            if e.errno == 57:
                pass
            else:
                traceback.print_exc()
    else:
        print("[System]: Trying to disconnect unknown worker")


# Function which parses newly brought message into separate lines and info
def parse_message(info_string):
    # There are three main blocks: processes, system and windows
    message_list_proc, message_list_integral, message_list_windows = info_string.split("\nNEW_INFO\n")
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

    # Now get information about windows
    opened_windows = []

    # Very primitive, but it works
    for line in message_list_windows:
        
        #if 'Current window name::::' in line:
            #current_window_name = line.split('::::')[1]
            #continue

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

        # All named info is described above. Only unnamed information is about 
        # opened windows, so code goes there only if everything else is read
        #if line:
            #opened_windows.append(line)

    return integral_node, processes


# Function which server connection
def break_connection(server_socket):
    for connection in connection_list:
        # First, we disconnect everyone else
        if connection == server_socket or connection == sys.stdin:
            continue
        connection.sendall("[System]: Closing connection...".encode(ENCODE))
        disconnect_client(connection)
    # And then shut down the server and killing the bot
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    print("[System]: Closing connection...")
    sys.exit(0)


def main():
    # First of all, configurate the server
    host = '192.168.0.105'
    port = 55555

    # AF_INET - internet socket, SOCK_STREAM - connection-based protocol for TCP, 
    # IPPROTO_TCP - choosing TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Check and turn on TCP Keepalive
    x = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
    if x == 0:
        x = server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Overrides value (in seconds) for keepalive
        server_socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, TCP_KEEPALIVE_TIMEOUT)

    try:
        # Assigning IP and port num to socket
        server_socket.bind((host, port))
    except socket.error:
        print("[System]: Socket bind failed!")
        traceback.print_exc()
        sys.exit(1)

    try:
        # Putting server into listening mode
        server_socket.listen(10)
    except socket.error:
        print("[System]: Socket listen failed!")
        traceback.print_exc()
        sys.exit(1)

    connection_list.append(server_socket)
    nicknames.append("Server")
    addresses.append( (host, port) )

    # We will need stdin, so also add it 
    connection_list.append(sys.stdin)
    nicknames.append("__stdin")
    addresses.append(0)

    print("[System]: Socket setup has been done!")

    db_existed = os.path.exists(DATABASE_NAME)
    if not db_existed:
        CreateDB.create_database(False)

    # Does not wait, but we don't need to, because kill it while closing connection
    if len(sys.argv) > 1 and sys.argv[1] == '--TGbot':
        global TGBot
        TGBot = subprocess.Popen("./TGBot.py")
        print("[System]: Telegram bot has been activated!")

    # Main loop
    try:
        while True:
            # Get the list of sockets that are ready to be read
            read_sockets, write_sockets, error_sockets = select.select(connection_list,[],[])

            # Process if we got data
            for sock in read_sockets:
                # New connection
                if sock == server_socket:
                    # Processing new client
                    client, address = server_socket.accept()
                    # Obtain a nickname of a new worker
                    nick = client.recv(BUFSIZE).decode(ENCODE)
                    # If there is already such name, decline the worker connection
                    if nick in nicknames:
                        disconnect_client(client)
                        continue

                    # Show message about new connection on server
                    print(f"[System]: New connection: ({nick}, {address})")
                    # Adding new worker to list of connections, names, and main dictionary
                    connection_list.append(client)
                    nicknames.append(nick)
                    addresses.append(address)
                    try:
                        DB_access.AddUser(DB_access.Session(), nick, nicknames.index(nick) - 1, f"{address}")
                    except:
                        pass

                # But if we got a data from stdin, it's likely to be message to break connection
                elif sock == sys.stdin:
                    command = sys.stdin.readline()
                    # But also it may just a mistake
                    if command in quit_list:
                        break_connection(server_socket)

                # Incoming message from a client
                else:
                    # Data received -> processing
                    try:
                        data = sock.recv(BUFSIZE)
                        if data.startswith(b'$'):
                            data = data.decode(ENCODE)
                            data = data[1:-1]
                            fileheader = data.split("_")
                            filename = fileheader[0]
                            filelength = int(fileheader[1])

                            sock.sendall("$filenamereceived$".encode(ENCODE))
                            file = open('n_' +filename, 'wb')
                            chunks = b''
                            bytes_recd = 0
                            while bytes_recd < filelength:
                                chunk = sock.recv(min(filelength - bytes_recd, BUFSIZE))
                                if chunk == b'':
                                    raise RuntimeError("socket connection broken")
                                chunks = chunks + chunk
                                bytes_recd = bytes_recd + len(chunk)

                            bytes_wrt = 0
                            try:
                                file.write(chunks)
                            except Exception:
                                traceback.print_exc()

                            file.close()
                            sock.sendall("$filereceived$".encode(ENCODE))

                            info_string = ""
                            file = open("./n_FileToSend.dat", "r")
                            info_string = file.read()
                            file.close()

                            nick = nicknames[connection_list.index(sock)]
                            # And parse all information
                            node, processes = parse_message(info_string)
                            try:
                                DB_access.AddComputerInfo(DB_access.Session(), nicknames.index(nick) - 1, node)

                                for process in processes:
                                    proc_node = {   'app_name': process[0],
                                                    'computer': nicknames.index(nick) - 1,
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

                    except:
                        traceback.print_exc()
                        continue
    except KeyboardInterrupt:
        # Cleaning everything in case of keyboard interruption
        break_connection(server_socket)
        if len(sys.argv) > 1 and sys.argv[1] == '--TGbot':
            TGBot.kill()

if __name__ == '__main__':
    main()