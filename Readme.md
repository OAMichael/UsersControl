### This repository created by [Pavel Filippenko](https://github.com/pavel-collab), [Mikhail Ovsiannikov](https://github.com/OAMichael) and [Barannikov Andrey](https://github.com/barannikovav).

### Понадобится установить следующее:
```console
pip install psutil
```
А также 
```console
pip install xprintidle
```

#### Пока что скрипт получает некоторую информацию о пользователе (работнике). Сначала он выводит для каждого процесса:
- PID
- Name
- Create time
- Cores
- CPU usage
- Status
- Nice value
- Memory consumption(rss) in bytes
- Memory consumption(vms) in bytes
- Memory consumption(shared) in bytes
- Memory consumption(data) in bytes
- Read bytes by process
- Written bytes by process
- Number of process's threads
- Username
- Parent PID
- Memory usage in percent
- Network connections

#### После всего этого выводится дополнительная информация о системе в целом:
- Disk memory usage
- CPU frequency(min) in MHz
- CPU frequency(max) in MHz
- CPU frequency(current) in MHz
- System boot time
- Total memory used by system in percent
- Every core and its temperatures in celsius degrees: current, high and critical
- Idle time
- Number of processes

#### Пример вывода:
```console
======================================================================
PID:                           8740
Name:                          Proj_get.py
Create time:                   2022-04-28 02:58:26.850000
Cores:                         8
CPU usage:                     0
Status:                        running
Nice value:                    0
Memory consumption(rss):       20131840
Memory consumption(vms):       32628736
Memory consumption(shared):    7782400
Memory consumption(data):      12787712
Read bytes:                    0
Written bytes:                 0
Number of threads:             1
Username:                      michael
PPID:                          1645
Memory percent:                0.3231724156069592
Network connections:           0
######################### Integral info ##############################
Disk memory usage:             60.9%
CPU frequency(min):            1400.0 MHz
CPU frequency(max):            2100.0 MHz
CPU frequency(current):        1336.632625 MHz
Boot time:                     2022-04-28 00:23:12
Total memory used:             43.1%
Core 0 tempereture:            current=68.000000°C, high=68.000000°C, critical=68.000000°C
Core 1 tempereture:            current=68.250000°C, high=68.250000°C, critical=68.250000°C
Core 2 tempereture:            current=68.250000°C, high=68.250000°C, critical=68.250000°C
Core 3 tempereture:            current=47.000000°C, high=47.000000°C, critical=47.000000°C
Idle time:                     0.753 s
Number of processes:           286
```

#### Пока что только вывод, но легко адаптировать под передачу на сервер, так как все поля легко достижимы.
