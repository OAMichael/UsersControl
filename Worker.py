#!/usr/bin/python3

import socket
import select
import traceback
import sys
import select
import psutil
from datetime import datetime, time
import time
import os
import warnings
from xdo import Xdo
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck
from client import TcpClient

# Connection Data
BUFSIZE = 2048
ENCODE = 'utf-8'
SOCKET_TIMEOUT = 2

# Command which persuade server to close connection
quit_list = ["quit\n", "Quit\n", "q\n", "exit\n", "Exit\n"]


info_string = ""


# ----------------------------------------------- Info about processes -----------------------------------------------
def get_processes_info():
    global info_string
    processes = []
    for process in psutil.process_iter():
        # get all process info in one shot
        with process.oneshot():

            # get the name of the process executed
            name = process.name()

            # get the time the process was spawned
            try:
                create_time = str(datetime.fromtimestamp(process.create_time()))
            except OSError:
                # system processes, using boot time instead
                create_time = str(datetime.fromtimestamp(psutil.boot_time()))
            
             # get the status of the process (running, idle, etc.)
            status = process.status()

            rss = 0
            vms = 0
            shared = 0
            data = 0
            try:
            # get the memory usage
                memory_usage = process.memory_full_info()
                rss    = memory_usage.rss
                vms    = memory_usage.vms
                shared = memory_usage.shared
                data   = memory_usage.data
            except psutil.AccessDenied:
                pass

            info_string = info_string + "{:s},{:s},{:s},{:d},{:d},{:d},{:d}\n".format(name, create_time, status,
                                                                                      rss, vms, shared, data)
            processes.append(name)
    
    info_string += "NEW_INFO\n"
    info_string += str(len(processes)) + "\n"


# ------------------------------------------- Info about system as a whole -------------------------------------------
def get_integral_info():
    global info_string
    # get CPU frequency
    cpu_freq = psutil.cpu_freq()

    # get boot time of system
    boot_time = datetime.fromtimestamp(psutil.boot_time())


    info = {'Disk memory usage':  str(psutil.disk_usage('/').percent), 'CPU frequency(min)': str(cpu_freq.min),
            'CPU frequency(max)': str(cpu_freq.max), 'CPU frequency(current)': str(cpu_freq.current), 
            'Boot time': boot_time, 'Total memory used': str(psutil.virtual_memory().percent)}

    # trying to obtain information about cores temperature
    try:
        temps = psutil.sensors_temperatures()
    except RuntimeWarning:
        pass

    if temps:
        num_of_cores = 0
        for name, entries in temps.items():
            for entry in entries:
                info[f'Core {num_of_cores} temperature'] = 'current={0:<6f}\N{DEGREE SIGN}C, high={0:<6f}\N{DEGREE SIGN}C, critical={0:<6f}\N{DEGREE SIGN}C'.format(entry.current, entry.high, entry.critical)
                num_of_cores += 1

    for inf in info:
        if not info[inf]:
            info[inf] = 0
        info_string += str(info[inf]) + "\n"

    return info


# ----------------------------------------------- Get list of windows ------------------------------------------------
def get_winlist():
    scr = Wnck.Screen.get_default()
    scr.force_update()
    windows = scr.get_windows()

    return windows


# ------------------------------------------------ Info about windows ------------------------------------------------
def get_win_info():
    global info_string
    info_string += "NEW_INFO\n"

    wlist = get_winlist()
    for w in wlist:
        info_string += w.get_name() + "\n"

    # Create an object of Xdo and then acquire information
    xdo = Xdo()

    # Active window
    try:
        xdo_window_id = xdo.get_active_window()
        xdo_window_name = xdo.get_window_name(xdo_window_id).decode('UTF-8')
        info_string += f"Current window id::::{str(xdo_window_id)}\n"
        info_string += f"Current window name::::{xdo_window_name}\n"

        time_activ.append((str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")), xdo_window_name))

        if xdo_window_name in win_activ.keys():
            win_activ[xdo_window_name] += 1
        else:
            win_activ[xdo_window_name] = 1
    except:
        pass

    # Now get information about most used windows
    values = list(win_activ.values())
    values_sorted = list(sorted(win_activ.values(), reverse=True))
    keys   = list(win_activ.keys())

    try:
        window_max_used_1  = keys[values.index(values_sorted[0])]
        max_used_percent_1 = values_sorted[0] / loop_times * 100
        info_string += f"Maximum used window::::{window_max_used_1}::::" + '{:0.2f}'.format(max_used_percent_1, 2) + "\n"
    except:
        pass

    # If there is a second used window
    try:
        k = values.index(values_sorted[1])
        window_max_used_2  = keys[k]
        while window_max_used_2 == window_max_used_1:
            k += 1
            window_max_used_2 = keys[k]

        max_used_percent_2 = values_sorted[1] / loop_times * 100
        info_string += f"Second maximum used window::::{window_max_used_2}::::" + '{:0.2f}'.format(max_used_percent_2, 2) + "\n"
    except:
        pass

    # If there is a third used window
    try:
        k = values.index(values_sorted[2])
        window_max_used_3  = keys[k]
        while window_max_used_3 == window_max_used_1 or window_max_used_3 == window_max_used_2:
            k += 1
            window_max_used_3 = keys[k]

        max_used_percent_3 = values_sorted[2] / loop_times * 100
        info_string += f"Third maximum used window::::{window_max_used_3}::::" + '{:0.2f}'.format(max_used_percent_3, 2) + "\n"
    except:
        pass

    # Get information about mouse location, especially which window mouse is over
    try:
        mouse_loc = xdo.get_mouse_location()
        info_string += f"Current mouse location::::" + f"({mouse_loc.x}, {mouse_loc.y})" + "\n"
    except:
        pass

    window_at_mouse_id = xdo.get_window_at_mouse()
    info_string += f"Window at mouse id::::" + str(window_at_mouse_id) + "\n"
    
    if window_at_mouse_id != 0:
        window_at_mouse_name = xdo.get_window_name(window_at_mouse_id).decode('UTF-8')
        info_string += f"Window at mouse name::::" + window_at_mouse_name + "\n"
    else:
        info_string += f"Window at mouse name::::" + "Root window" + "\n"


# function with obtaining all info
def main_iteration():
#-------------------------------------------- Processes info --------------------------------------------#
    get_processes_info()
#--------------------------------------- System and computer info ---------------------------------------#
    get_integral_info()
#--------------------------------------------- Windows info ---------------------------------------------#
    get_win_info()


def main():

    nickname = str(input("Enter your name: "))
    # Getting connection info
    host = '172.20.10.13'
    port = 55555

    # Connecting to server

    # AF_INET - internet socket, SOCK_STREAM - connection-based protocol for TCP, 
    # IPPROTO_TCP - choosing TCP
    # 5-second timeout to detect errors
    #try:
    #    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    #    client_socket.settimeout(SOCKET_TIMEOUT)
    #except:
    #    print("Error creating socket!")
    #    traceback.print_exc()
    #    sys.exit(1)

    # Check and turn on TCP Keepalive
    #try:
    #    x = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
    #    if (x == 0):
    #        x = client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    #        # Overrides value (in seconds) for keepalive
    #        client_socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 300)
    #except:
    #    print("Error processing TCP Keepalive!")
    #    traceback.print_exc()
    #    sys.exit(1)   

    # Connect to host
    #try: 
    #    client_socket.connect((host, port))
    #except Exception as e:
    #    if e.errno != 36:
    #        print ("Socket connect failed!")
    #        traceback.print_exc()
    #        sys.exit(1)


    worker = TcpClient(host, port)


    warnings.filterwarnings("ignore")
    global info_string

    # dictionary with {"[window name] : [activity percentage]"}
    global win_activ    
    win_activ = {}

    # list with node as [datetime, active window]
    global time_activ
    time_activ = []

    # number of iterations
    global loop_times
    loop_times = 0

    # Send to server nickname of THIS computer's worker
    try:
        worker.sendmsg(nickname)
    except:
        pass

    try:
        # loop everything and sleep for 5 seconds
        while True:
            loop_times += 1
            main_iteration()
            #client_socket.sendall(info_string.encode(ENCODE))
            file = open("./FileToSend.dat", "w")
            file.write(info_string)
            file.close()
            file = open("./FileToSend.dat", "rb")
            worker.sendfile("./FileToSend.dat", file)
            file.close()
            info_string = ""
            
            #if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            #    command = sys.stdin.readline()
            #    # If we type quit command
            #    if command in quit_list:
            #        print("[System]: Closing connection...")
            #        break
            time.sleep(5)

    except KeyboardInterrupt:
        # Cleaning everything in case of keyboard interruption
        #client_socket.shutdown(socket.SHUT_RDWR)
        #client_socket.close()
        pass

if __name__ == '__main__':
    main()