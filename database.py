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

    # закрываем содинение
    conn.close()
