import sqlite3
from os.path import exists
from sys import exit

def CreateDict(data: tuple) -> dict:
    dict_data = {}
    keys = ['Name', 'Create_Time', 'Status', 'Mem_cons_rss', 'Mem_cons_vms', 'Mem_cons_shared', 'Mem_cons_data']
    if len(keys) != len(data):
        print('error, keys and data are not the same len')
        exit(1)
    
    for i in range(len(keys)):
        dict_data[keys[i]] = data[i]
        
    return dict_data

def WriteToDB(data: tuple):
    # если базы данных не существует, ее нужно создать
    if not exists('Local_DB.s3db'):
        print("this data base already exists")
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
    
    # если файл уже существует, значит в таблице уже хранятся данные, не надо ее пересоздавать
    # Создаем соединение с нашей базой данных
    conn = sqlite3.connect('Local_DB.s3db')
    # Создаем курсор
    cursor = conn.cursor()

    # из кортежа с данными создаем список
    dict_data = CreateDict(data)
    cursor.execute("""
                INSERT INTO 
                t1(Name, Create_Time, Status, Mem_cons_rss, Mem_cons_vms, Mem_cons_shared, Mem_cons_data) 
                VALUES 
                (:Name, :Create_Time, :Status, :Mem_cons_rss, :Mem_cons_vms, :Mem_cons_shared, :Mem_cons_data)""", 
                dict_data)

    # сохраняем транзакцию
    conn.commit()
    # закрываем содинение
    conn.close()
