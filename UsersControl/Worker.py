#!/usr/bin/python3

import random
import string
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
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck
from client_async import TcpClient

if sys.platform == 'linux' or sys.platform == 'linux2':
    from xdo import Xdo
elif sys.platform == 'darwin':
    from xdo import xdo as Xdo
else:
    raise NotImplemented



# ----------------------------------------------- Info about processes -----------------------------------------------
def get_processes_info():
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

            processes.append( [name, 
                               create_time,
                               status,
                               rss,
                               vms,
                               shared,
                               data] )

    return processes


# ------------------------------------------- Info about system as a whole -------------------------------------------
def get_integral_info():
    global integral_node
    # get CPU frequency
    cpu_freq = psutil.cpu_freq()

    # get boot time of system
    boot_time = datetime.fromtimestamp(psutil.boot_time())

    integral_node['disk_mem_usege'] = str(psutil.disk_usage('/').percent) 
    integral_node['CPU_f_min'] = '{:0.2f}'.format(cpu_freq.min, 2)
    integral_node['CPU_f_max'] = '{:0.2f}'.format(cpu_freq.max, 2) 
    integral_node['CPU_f_cur'] = '{:0.2f}'.format(cpu_freq.current, 2) 
    integral_node['Boot_time'] = str(boot_time) 
    integral_node['Total_mem_used'] = str(psutil.virtual_memory().percent)


# ----------------------------------------------- Get list of windows ------------------------------------------------
def get_winlist():
    scr = Wnck.Screen.get_default()
    scr.force_update()
    windows = scr.get_windows()

    return windows


# ------------------------------------------------ Info about windows ------------------------------------------------
def get_win_info():
    global integral_node
    global window_pids
    # Create an object of Xdo and then acquire information
    xdo = Xdo()

    wlist = get_winlist()
    for w in wlist:
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
        integral_node['curent_window_active'] = xdo_window_name

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
        integral_node['first_window']         = window_max_used_1
        integral_node['first_window_percent'] = '{:0.2f}'.format(max_used_percent_1, 2)
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
        integral_node['second_window']         = window_max_used_2
        integral_node['second_window_percent'] = '{:0.2f}'.format(max_used_percent_2, 2)
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
        integral_node['third_window']         = window_max_used_3
        integral_node['third_window_percent'] = '{:0.2f}'.format(max_used_percent_3, 2)
    except:
        pass

# function with obtaining all info
def main_iteration():
#--------------------------------------------- Windows info ---------------------------------------------#
    get_win_info()
#-------------------------------------------- Processes info --------------------------------------------#
    processes = get_processes_info()
#--------------------------------------- System and computer info ---------------------------------------#
    get_integral_info()
    return processes


def generate_machine_id():
    machine_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    return machine_id


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [config_path]")
        sys.exit(1)

    # Getting connection info
    with open(sys.argv[1], "r+") as file:
        host = file.readline().strip("\n").split("host = ")[1]
        port = int(file.readline().strip("\n").split("port = ")[1])
        global nickname
        nickname = file.readline().strip("\n").split("nickname = ")[1]
        machine_id_raw = file.readline().strip("\n").split("machine id = ")
        if len(machine_id_raw) < 2 or machine_id_raw[1] == '':
            machine_id = generate_machine_id()
            file.write(machine_id)
        else:
            machine_id = machine_id_raw[1] 
    
    # Connecting to server
    worker = TcpClient(host, port, nickname, machine_id)

    global integral_node
    integral_node = { 'first_window': "None",
                      'first_window_percent': 0,
                      'second_window': "None",
                      'second_window_percent': 0,
                      'third_window': "None",
                      'third_window_percent': 0
                      }

    global window_pids
    window_pids = []

    # dictionary with {"[window name] : [activity percentage]"}
    global win_activ    
    win_activ = {}

    # number of iterations
    global loop_times
    loop_times = 0

    try:
        # loop everything and sleep for 5 seconds
        while True:
            loop_times += 1
            processes = main_iteration()
            integral_node['proc_number'] = len(processes)            
            worker.senddata( (integral_node, processes) )
            time.sleep(5)
    except:
        print("Closing connection...")
        pass

if __name__ == '__main__':
    main()