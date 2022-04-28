#!/usr/bin/python3

import sys
import psutil
from datetime import datetime
import time
import os
import warnings
import xprintidle

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

    warnings.filterwarnings("ignore")
    
    processes = get_processes_info()

    for proc in processes:
        print('======================================================================')
        for info in proc:
            if not proc[info]:
                proc[info] = 0
            print("{0:<30s}".format(info + ':'), proc[info])

    print("######################### Integral info ##############################")
    integral_info = get_integral_info()
    for info in integral_info:
        if not integral_info[info]:
            integral_info[info] = 0
        print("{0:<30s}".format(info + ':'), integral_info[info])


    milliseconds_string = os.popen("xprintidle").read()
    seconds = int(milliseconds_string) // 1000
    milliseconds = int(milliseconds_string) - seconds * 1000
    print("{0:<30s}".format('Idle time:'), f'{seconds}.{milliseconds} s')
    #print(milliseconds_string)
    print("{0:<30s}".format("Number of processes:"), len(processes))



if __name__ == '__main__':
    main()