#!/usr/bin/python3

import socket
import select
import traceback
import sys
import subprocess
import time
from collections import deque

# module to perform database operations
import DB_modul


# Connection Data
BUFSIZE = 32768
ENCODE = 'utf-8'
TCP_KEEPALIVE_TIMEOUT = 300
QUEUELEN = 10


# Lists for program work

connection_list = []
nicknames = []
addresses = []
workers = {}
quit_list = ["quit\n", "Quit\n", "q\n", "exit\n", "Exit\n"]


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
        print("[System]: Trying to disconnect unknown worker")



def parse_message(info_string):
    
    message_list_proc, message_list_integral, message_list_windows = info_string.split("\nNEW_INFO\n")
    message_list_proc     = message_list_proc.split("\n")
    message_list_integral = message_list_integral.split("\n")
    message_list_windows  = message_list_windows.split("\n")
    processes = []

    for line in message_list_proc:
        processes.append(tuple(line.split(",")))

    integral_info = { 'Number of processes': message_list_integral[0], 
                      'Disk memory usage':  message_list_integral[1], 
                      'CPU frequency(min)': message_list_integral[2],
                      'CPU frequency(max)': message_list_integral[3], 
                      'CPU frequency(current)': message_list_integral[4], 
                      'Boot time': message_list_integral[5], 
                      'Total memory used': message_list_integral[6]  }

    if len(message_list_integral) > 7:
        for n in range(7, len(message_list_integral)):
            integral_info[f'Core {n - 7} temperature'] = message_list_integral[n]

    opened_windows = []
    max_used_percent_2 = 0
    max_used_percent_3 = 0
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

        if line:
            opened_windows.append(line)

    work_info = { "Processes"             : processes, 
                  "Integral info"         : integral_info, 
                  "Opened windows"        : opened_windows,
                  "Current window id"     : current_window_id, 
                  "Current window name"   : current_window_name,
                  "Maximum used window"   : window_max_used_1,
                  "Max used percent 1"    : max_used_percent_1,
                  "Current mouse location": current_mouse_location,
                  "Window at mouse id"    : window_at_mouse_id,
                  "window_at_mouse_name"  : window_at_mouse_name}

    if max_used_percent_2:
        work_info["Maximum used window 2"] = window_max_used_2
        work_info["Max used percent 2"]    = max_used_percent_2

    if max_used_percent_3:
        work_info["Maximum used window 3"] = window_max_used_3
        work_info["Max used percent 3"]    = max_used_percent_3

    return work_info


def main():
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

    connection_list.append(sys.stdin)
    nicknames.append("STDIN")
    addresses.append(0)

    print("[System]: Socket setup has been done!")

    # Does not wait
    TGBot = subprocess.Popen("./TGBot.py")
    print("[System]: Telegram bot has been activated!")

    file = open("./Names.dat", "w")
    file.write("")
    file.close()

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
                    nick = client.recv(BUFSIZE).decode(ENCODE)
                    print(f"[System]: New connection: ({nick}, {str(address)})")
                    connection_list.append(client)
                    file = open("./Names.dat", "a")
                    file.write(nick)
                    file.close()
                    nicknames.append(nick)
                    workers[nick] = {}
                    addresses.append(address)

                elif sock == sys.stdin:
                    command = sys.stdin.readline()
                    if command in quit_list:
                        server_socket.shutdown(socket.SHUT_RDWR)
                        server_socket.close()
                        TGBot.kill()
                        print("[System]: Closing connection...")
                        return

                # Incoming message from a client
                else:
                    # Data received -> processing
                    try:
                        message = sock.recv(BUFSIZE)
                        if message:
                            nick = nicknames[connection_list.index(sock)]
                            workers[nick] = parse_message(message.decode(ENCODE))

                            lines = [workers[nick]["Maximum used window"] + "\n", workers[nick]["Max used percent 1"] + "\n"]

                            if "Maximum used window 2" in workers[nick]:
                                lines.append(workers[nick]["Maximum used window 2"] + "\n")
                                lines.append(workers[nick]["Max used percent 2"] + "\n")

                            if "Maximum used window 3" in workers[nick]:
                                lines.append(workers[nick]["Maximum used window 3"] + "\n")
                                lines.append(workers[nick]["Max used percent 3"])

                            file = open("./Hists/Hist" + nick + ".dat", "w")
                            file.writelines(lines)
                            file.close()

                            ## write information about every process into database
                            #for proc in workers[nick]["Processes"]:
                            #    DB_modul.WriteToDB(proc)
                    except:
                        traceback.print_exc()
                        continue
    except KeyboardInterrupt:
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()
        TGBot.kill()
        TGBot.kill()
        print("[System]: Closing connection...")


if __name__ == '__main__':
    main()