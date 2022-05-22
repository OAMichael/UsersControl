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
SOCKET_TIMEOUT = 5

# ----------------------------------------------- Info about processes -----------------------------------------------
def get_processes_info():
    info_string = "NEW_INFO\n"
    processes = []
    global window_pids
    for process in psutil.process_iter():
        # get all process info in one shot
        with process.oneshot():
            # Obtain information only about processes of windows
            if process.pid not in window_pids:
                continue

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

    file = open("./FileToSend.dat", "a")
    file.write(info_string)
    file.close()


# ------------------------------------------- Info about system as a whole -------------------------------------------
def get_integral_info():
    info_string = ""
    # get CPU frequency
    cpu_freq = psutil.cpu_freq()

    # get boot time of system
    boot_time = datetime.fromtimestamp(psutil.boot_time())


    info = {'Disk memory usage':  str(psutil.disk_usage('/').percent), 'CPU frequency(min)': '{:0.2f}'.format(cpu_freq.min, 2),
            'CPU frequency(max)': '{:0.2f}'.format(cpu_freq.max, 2), 'CPU frequency(current)': '{:0.2f}'.format(cpu_freq.current, 2), 
            'Boot time': boot_time, 'Total memory used': str(psutil.virtual_memory().percent)}

    for inf in info:
        if not info[inf]:
            info[inf] = 0
        info_string += str(info[inf]) + "\n"

    file = open("./FileToSend.dat", "a")
    file.write(info_string)
    file.close()

# ----------------------------------------------- Get list of windows ------------------------------------------------
def get_winlist():
    scr = Wnck.Screen.get_default()
    scr.force_update()
    windows = scr.get_windows()

    return windows


# ------------------------------------------------ Info about windows ------------------------------------------------
def get_win_info():
    info_string = ""
    global window_pids
    # Create an object of Xdo and then acquire information
    xdo = Xdo()

    wlist = get_winlist()
    for w in wlist:
        info_string += w.get_name() + "\n"
        new_name = w.get_name().encode()
        new_windows = xdo.search_windows(winname=new_name)
        if new_windows:
            for window in new_windows:
                new_pid = xdo.get_pid_window(window)
                if new_pid != 0 and new_pid not in window_pids: 
                    window_pids.append(new_pid)

    # Active window
    try:
        xdo_window_name = xdo.get_window_name(xdo.get_active_window()).decode('UTF-8')
        info_string += f"Current window name::::{xdo_window_name}\n"

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

    file = open("./FileToSend.dat", "w")
    file.write(info_string)
    file.close()


# function with obtaining all info
def main_iteration():
#--------------------------------------------- Windows info ---------------------------------------------#
    get_win_info()
#-------------------------------------------- Processes info --------------------------------------------#
    get_processes_info()
#--------------------------------------- System and computer info ---------------------------------------#
    get_integral_info()



def main():
    
    # Getting connection info
    host = str(input("Enter main server host: "))
    port = int(input("Enter port: "))
    nickname = str(input("Enter your name: "))

    # Connecting to server
    worker = TcpClient(host, port)

    warnings.filterwarnings("ignore")

    global window_pids
    window_pids = []

    # dictionary with {"[window name] : [activity percentage]"}
    global win_activ    
    win_activ = {}

    # number of iterations
    global loop_times
    loop_times = 0

    # Send to server nickname of THIS computer's worker
    worker.sendmsg(nickname)

    try:
        # loop everything and sleep for 5 seconds
        while True:
            loop_times += 1
            main_iteration()
            file = open("FileToSend.dat", "rb")
            worker.sendfile("FileToSend.dat", file)
            file.close()
            time.sleep(5)

    except:
        print("Closing connection...")
        os.remove("FileToSend.dat")
        pass

if __name__ == '__main__':
    main()