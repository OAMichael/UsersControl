#!/usr/bin/python3
# Импортируем библиотеку 
import sqlite3
from os.path import exists
from sys import exit

if exists('Local_DB.s3db'):
    print("this data base already exists")

    # Создаем соединение с нашей базой данных
    conn = sqlite3.connect('Local_DB.s3db')
    # Создаем курсор
    cur = conn.cursor()      
    cur.execute('SELECT * FROM t1')
    print(cur.fetchall()) # возвращает список
    exit(1) 

# Создаем соединение с нашей базой данных
conn = sqlite3.connect('Local_DB.s3db')

# Создаем курсор
cursor = conn.cursor()

cursor.execute("""CREATE TABLE t1(
            Name TEXT,
            Create_Time TEXT,
            Status TEXT,
            Mem_cons_rss INTEGER,
            Mem_cons_vms INTEGER,
            Mem_cons_shared INTEGER,
            Mem_cons_data INTEGER
            )""")


cursor.execute("""
                INSERT INTO 
                t1(Name, Create_Time, Status, Mem_cons_rss, Mem_cons_vms, Mem_cons_shared, Mem_cons_data) 
                VALUES 
                (:Name, :Create_Time, :Status, :Mem_cons_rss, :Mem_cons_vms, :Mem_cons_shared, :Mem_cons_data)""", 
                {'Name':'Proj_get.py', 
                'Create_Time':'2022-05-04 17:27:05.320000', 
                'Status':'running', 
                'Mem_cons_rss':23478272, 'Mem_cons_vms':31801344, 'Mem_cons_shared':7557120, 'Mem_cons_data':16384000})

# сохраняем транзакцию
conn.commit()
# закрываем содинение
conn.close()