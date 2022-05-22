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
workers = {}

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
    integral_info = { 'Number of processes': message_list_integral[0], 
                      'Disk memory usage':  message_list_integral[1], 
                      'CPU frequency(min)': message_list_integral[2],
                      'CPU frequency(max)': message_list_integral[3], 
                      'CPU frequency(current)': message_list_integral[4], 
                      'Boot time': message_list_integral[5], 
                      'Total memory used': message_list_integral[6]  }

    # Case of additional info about cores' temperature
    if len(message_list_integral) > 7:
        for n in range(7, len(message_list_integral)):
            integral_info[f'Core {n - 7} temperature'] = message_list_integral[n]

    # Now get information about windows
    opened_windows = []
    max_used_percent_2 = 0
    max_used_percent_3 = 0

    # Very primitive, but it works
    for line in message_list_windows:
        if 'Current window id::::' in line:
            current_window_id = line.split('::::')[1]
            continue
        
        if 'Current window name::::' in line:
            current_window_name = line.split('::::')[1]
            continue

        if 'Maximum used window::::' in line:
            window_max_used_1  = line.split('::::')[1]
            max_used_percent_1 = line.split('::::')[2]
            continue

        if 'Second maximum used window::::' in line:
            window_max_used_2  = line.split('::::')[1]
            max_used_percent_2 = line.split('::::')[2]
            continue

        if 'Third maximum used window::::' in line:
            window_max_used_3  = line.split('::::')[1]
            max_used_percent_3 = line.split('::::')[2]
            continue

        if 'Current mouse location::::' in line:
            current_mouse_location = line.split('::::')[1]
            continue

        if 'Window at mouse id::::' in line:
            window_at_mouse_id = line.split('::::')[1] 
            continue

        if 'Window at mouse name::::' in line:
            window_at_mouse_name = line.split('::::')[1]
            continue

        # All named info is described above. Only unnamed information is about 
        # opened windows, so code goes there only if everything else is read
        if line:
            opened_windows.append(line)

    # Now assemble everything into one dictionary which will be a value-node for a main dict
    work_info = { "Processes"             : processes, 
                  "Integral info"         : integral_info, 
                  "Opened windows"        : opened_windows,
                  "Current window id"     : current_window_id, 
                  "Current window name"   : current_window_name,
                  "Maximum used window"   : window_max_used_1,
                  "Max used percent 1"    : max_used_percent_1,
                  "Current mouse location": current_mouse_location,
                  "Window at mouse id"    : window_at_mouse_id,
                  "window_at_mouse_name"  : window_at_mouse_name }

    # If there any
    if max_used_percent_2:
        work_info["Maximum used window 2"] = window_max_used_2
        work_info["Max used percent 2"]    = max_used_percent_2

    if max_used_percent_3:
        work_info["Maximum used window 3"] = window_max_used_3
        work_info["Max used percent 3"]    = max_used_percent_3

    return work_info


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
    if len(sys.argv) > 1 and sys.argv[1] == '-TGbot':
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
                        #client.sendall("[Server]: Sorry, but this nickname already exists. Try another one.".encode(ENCODE))
                        disconnect_client(client)
                        continue
                    #else:
                        # And if there isn't, accept new user
                        #client.sendall("[Server]: Great nickname. Welcome aboard.".encode(ENCODE))
                    # Show message about new connection on server
                    print(f"[System]: New connection: ({nick}, {str(address)})")
                    # Adding new worker to list of connections, names, and main dictionary
                    connection_list.append(client)
                    nicknames.append(nick)
                    workers[nick] = {}
                    addresses.append(address)
                    DB_access.AddUser(DB_access.Session(), nick, nicknames.index(nick) - 1)

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
                            workers[nick] = parse_message(info_string)

                            node = (workers[nick]["Maximum used window"], 
                                    workers[nick]["Maximum used window 2"] if "Maximum used window 2" in workers[nick] else "None", 
                                    workers[nick]["Maximum used window 3"] if "Maximum used window 3" in workers[nick] else "None", 
                                    float(workers[nick]["Max used percent 1"]),
                                    float(workers[nick]["Max used percent 2"]) if "Max used percent 2" in workers[nick] else 0,
                                    float(workers[nick]["Max used percent 3"]) if "Max used percent 3" in workers[nick] else 0,
                                    int(workers[nick]["Integral info"]["Number of processes"]),
                                    float(workers[nick]["Integral info"]["Disk memory usage"]),
                                    float(workers[nick]["Integral info"]["CPU frequency(min)"]),
                                    float(workers[nick]["Integral info"]["CPU frequency(max)"]),
                                    float(workers[nick]["Integral info"]["CPU frequency(current)"]),
                                    str(workers[nick]["Integral info"]["Boot time"]),
                                    float(workers[nick]["Integral info"]["Total memory used"]),
                                    datetime.now() )

                            DB_access.AddComputerInfo(DB_access.Session(), nicknames.index(nick) - 1, node)

                    except:
                        traceback.print_exc()
                        continue
    except KeyboardInterrupt:
        # Cleaning everything in case of keyboard interruption
        break_connection(server_socket)
        if len(sys.argv) > 1 and sys.argv[1] == '-TGbot':
            TGBot.kill()

if __name__ == '__main__':
    main()