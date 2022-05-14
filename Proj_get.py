#!/usr/bin/python3

import sys
import psutil
from datetime import datetime, time
import time
import os
import warnings
from xdo import Xdo
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck
import subprocess


# modulus to perform database operations
import DB_modul

def get_processes_info():
    processes = []
    for process in psutil.process_iter():
        # get all process info in one shot
        with process.oneshot():

            # get the name of the file executed (string)
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

            processes.append(tuple( (name, create_time, status, rss, vms, shared, data) ))

    return processes

def get_integral_info():
    # get CPU frequency
    cpu_freq = psutil.cpu_freq()

    # get boot time of system
    boot_time = datetime.fromtimestamp(psutil.boot_time())


    info = {'Disk memory usage':  str(psutil.disk_usage('/').percent) + '%', 'CPU frequency(min)': str(cpu_freq.min) + ' MHz',
            'CPU frequency(max)': str(cpu_freq.max) + ' MHz',                'CPU frequency(current)': str(cpu_freq.current) + ' MHz', 
            'Boot time': boot_time, 'Total memory used': str(psutil.virtual_memory().percent) + '%'}

    # trying to obtain information about cores temperature
    try:
        temps = psutil.sensors_temperatures()
    except RuntimeWarning:
        pass

    if not temps:
        return info

    num_of_cores = 0
    for name, entries in temps.items():
        for entry in entries:
            info[f'Core {num_of_cores} tempereture'] = 'current={0:<6f}\N{DEGREE SIGN}C, high={0:<6f}\N{DEGREE SIGN}C, critical={0:<6f}\N{DEGREE SIGN}C'.format(entry.current, entry.high, entry.critical)
            num_of_cores += 1

    return info

# Get the window list
def get_winlist():
    scr = Wnck.Screen.get_default()
    scr.force_update()
    windows = scr.get_windows()

    return windows

# function with obtaining and printing(for debug) all info
def main_iteration():
#-------------------------------------------- Processes info --------------------------------------------#
    processes = get_processes_info()

    for proc in processes:
        # write information about every process into database
        DB_modul.WriteToDB(proc)
        print(proc)

    print("{0:<30s}".format("Number of processes:"), len(processes))

#--------------------------------------- System and computer info ---------------------------------------#

    print("######################### Integral info ##############################")
    integral_info = get_integral_info()
    for info in integral_info:
        if not integral_info[info]:
            integral_info[info] = 0
        print("{0:<30s}".format(info + ':'), integral_info[info])


#--------------------------------------------- Windows info ---------------------------------------------#

    print("######################### Opened windows #############################")

    wlist = get_winlist()
    for w in wlist:
        print(w.get_name())

    print("######################### Current window #############################")
    # Create an object of Xdo and then acquire information
    xdo = Xdo()

    # Active window
    try:
        xdo_window_id = xdo.get_active_window()
        xdo_window_name = xdo.get_window_name(xdo_window_id).decode('UTF-8')
        print("{0:<30s}".format("Current window id:"), xdo_window_id)
        print("{0:<30s}".format("Current window name:"), xdo_window_name)


        if xdo_window_name in win_activ.keys():
            win_activ[xdo_window_name] += 1
        else:
            win_activ[xdo_window_name] = 1
    except:
        pass

    time_activ.append((str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")), xdo_window_name))

    # Now get information about most used windows

    values = list(win_activ.values())
    values_sorted = list(sorted(win_activ.values(), reverse=True))
    keys   = list(win_activ.keys())

    # Opening file
    file = open("./Hist.dat", "w")

    try:
        window_max_used_1  = keys[values.index(values_sorted[0])]
        max_used_percent_1 = values_sorted[0] / loop_times * 100
        print('{0:<30s}'.format("Maximum used window:"), window_max_used_1, '{:0.2f}%'.format(max_used_percent_1, 2))

        file.write(window_max_used_1  + "\n")
        file.write(str(max_used_percent_1) + "\n")
    except:
        pass

    try:
        k = values.index(values_sorted[1])
        window_max_used_2  = keys[k]
        while window_max_used_2 == window_max_used_1:
            k += 1
            window_max_used_2 = keys[k]

        max_used_percent_2 = values_sorted[1] / loop_times * 100
        print('{0:<30s}'.format("Second maximum used window:"), window_max_used_2, '{:0.2f}%'.format(max_used_percent_2, 2))

        file.write(window_max_used_2  + "\n")
        file.write(str(max_used_percent_2) + "\n")
    except:
        pass

    try:
        k = values.index(values_sorted[2])
        window_max_used_3  = keys[k]
        while window_max_used_3 == window_max_used_1 or window_max_used_3 == window_max_used_2:
            k += 1
            window_max_used_3 = keys[k]

        max_used_percent_3 = values_sorted[2] / loop_times * 100
        print('{0:<30s}'.format("Third maximum used window:"), window_max_used_3, '{:0.2f}%'.format(max_used_percent_3, 2))

        file.write(window_max_used_3  + "\n")
        file.write(str(max_used_percent_3) + "\n")
    except:
        pass

    # Closing file
    file.close()

    # Get information about mouse location, especially which window mouse is over
    try:
        mouse_loc = xdo.get_mouse_location()
        print("{0:<30s}".format("Current mouse location:"), f"({mouse_loc.x}, {mouse_loc.y})")
    except:
        pass

    window_at_mouse_id   = xdo.get_window_at_mouse()
    print("{0:<30s}".format("Window at mouse id:"),   window_at_mouse_id)
    
    if window_at_mouse_id != 0:
        window_at_mouse_name = xdo.get_window_name(window_at_mouse_id).decode('UTF-8')
        print("{0:<30s}".format("Window at mouse name:"), window_at_mouse_name)
    else:
        print("{0:<30s}".format("Window at mouse name:"), "Root window")



def main():

    warnings.filterwarnings("ignore")

    # dictionary with {"[window name] : [activity percentage]"}
    global win_activ    
    win_activ = {}

    # list with node as [datetime, active window]
    global time_activ
    time_activ = []

    # number of iterations
    global loop_times
    loop_times = 0

    # Does not wait
    TGBot = subprocess.Popen("./TGBot.py")

    # loop everything and sleep for 5 seconds
    while True:
        loop_times += 1
        main_iteration()
        time.sleep(5)

if __name__ == '__main__':
    main()