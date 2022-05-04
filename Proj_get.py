#!/usr/bin/python3

import sys
import psutil
from datetime import datetime
import time
import os
import warnings
from xdo import Xdo

# модуль с функциями обработки базы данных
import DB_modul

def get_processes_info():
    processes = []
    for process in psutil.process_iter():
        # get all process info in one shot
        with process.oneshot():
            # get the process id
            pid = process.pid
            if pid == 0:
                continue


            try:
                # Parent pid (number)
                ppid = process.ppid()
            except psutil.AccessDenied:
                ppid = 0

            try:
                # get the number of total threads spawned by this process
                n_threads = process.num_threads()
            except psutil.AccessDenied:
                n_threads = 1


            try:
                # Number of fds (number)
                fds  = process.num_fds()
            except psutil.AccessDenied:
                fds = 0

            # Percentage (number)
            memory_percent = process.memory_percent()

            try:
                # List of named tuples
                connections = process.connections()
            except psutil.AccessDenied:
                connections = 0

            # get the name of the file executed (string)
            name = process.name()

            # get the time the process was spawned
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                # system processes, using boot time instead
                create_time = datetime.fromtimestamp(psutil.boot_time())
            

            try:
            # get the number of CPU cores that can execute this process
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0
            
            # get the CPU usage percentage (number)
            cpu_usage = process.cpu_percent()

             # get the status of the process (running, idle, etc.) (string)
            status = process.status()


            try:
            # get the process priority (a lower value means a more prioritized process) (number)
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0
            
            rss = 0
            vms = 0
            shared = 0
            data = 0
            try:
            # get the memory usage (list or tuple)
                memory_usage = process.memory_full_info()
                rss    = memory_usage.rss
                vms    = memory_usage.vms
                shared = memory_usage.shared
                data   = memory_usage.data
            except psutil.AccessDenied:
                pass

            try:
                # total process read and written bytes (number)
                io_counters = process.io_counters()
                read_bytes  = io_counters.read_bytes
                write_bytes = io_counters.write_bytes
            except:
                read_bytes  = 0
                write_bytes = 0


            # get the username of user spawned the process (string)
            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"

            processes.append({ 'PID': pid, 'Name': name, 'Create time': create_time,
            'Cores': cores, 'CPU usage': cpu_usage, 'Status': status, 'Nice value': nice,
            'Memory consumption(rss)': rss, 'Memory consumption(vms)': vms, 'Memory consumption(shared)': shared,
            'Memory consumption(data)': data, 'Read bytes': read_bytes, 'Written bytes': write_bytes,
            'Number of threads': n_threads, 'Username': username, 'PPID': ppid, 
            'Memory percent': memory_percent, 'Network connections': connections,
        })

    return processes

def get_processes_info_reduced():
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
            
             # get the status of the process (running, idle, etc.) (string)
            status = process.status()

            rss = 0
            vms = 0
            shared = 0
            data = 0
            try:
            # get the memory usage (list or tuple)
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
    cpu_freq = psutil.cpu_freq()
    boot_time = datetime.fromtimestamp(psutil.boot_time())


    info = {'Disk memory usage':  str(psutil.disk_usage('/').percent) + '%', 'CPU frequency(min)': str(cpu_freq.min) + ' MHz',
            'CPU frequency(max)': str(cpu_freq.max) + ' MHz',                'CPU frequency(current)': str(cpu_freq.current) + ' MHz', 
            'Boot time': boot_time, 'Total memory used': str(psutil.virtual_memory().percent) + '%'}

    try:
        temps = psutil.sensors_temperatures()
    except RuntimeWarning:
        pass

    if not temps:
        return info

    n = 0
    for name, entries in temps.items():
        for entry in entries:
            info[f'Core {n} tempereture'] = 'current={0:<6f}\N{DEGREE SIGN}C, high={0:<6f}\N{DEGREE SIGN}C, critical={0:<6f}\N{DEGREE SIGN}C'.format(entry.current, entry.high, entry.critical)
            n += 1

    return info


def main():

    #while True:
    warnings.filterwarnings("ignore")
    
    processes = get_processes_info_reduced()

    for proc in processes:
        # запись информации о каждом процессе в базу данных
        DB_modul.WriteToDB(proc)
        print(proc)

    print("######################### Integral info ##############################")
    integral_info = get_integral_info()
    for info in integral_info:
        if not integral_info[info]:
            integral_info[info] = 0
        print("{0:<30s}".format(info + ':'), integral_info[info])


    print("{0:<30s}".format("Number of processes:"), len(processes))



    xdo = Xdo()
    
    try:
        xdo_window_id = xdo.get_active_window()
        xdo_window_name = xdo.get_window_name(xdo_window_id).decode('UTF-8')
        print("{0:<30s}".format("Current window id:"), xdo_window_id)
        print("{0:<30s}".format("Current window name:"), xdo_window_name)
    except:
        pass

    mouse_loc = xdo.get_mouse_location()
    print("{0:<30s}".format("Current mouse location:"), f"({mouse_loc.x}, {mouse_loc.y})")

    try:
        window_at_mouse_id   = xdo.get_window_at_mouse()
        window_at_mouse_name = xdo.get_window_name(window_at_mouse_id).decode('UTF-8')

        print("{0:<30s}".format("Window at mouse id:"),   window_at_mouse_id)
        print("{0:<30s}".format("Window at mouse name:"), window_at_mouse_name)
    except:
        pass

        #time.sleep(5)

if __name__ == '__main__':
    main()