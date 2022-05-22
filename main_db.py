#!/usr/bin/python3

import os
from models.Database import DATABASE_NAME
from models.Database import Session
import CreateDB as db_creator
import datetime

import DB_access

if __name__ == '__main__':
    
    db_existed = os.path.exists(DATABASE_NAME)
    if not db_existed:
        db_creator.create_database(True)

    '''Your code here'''

    # DB_access.AddApplication(Session(), 'ddd', 4)
    # DB_access.TakeAppsList(Session(), 'Евпраксия Борисовна Панова')

    # list1, list2 = DB_access.MostUsasbleWindows(Session(), 'Ратибор Даниилович Фокин')
    # print(list1)
    # print(list2)

# посмотреть табличку в приложении
#* sqlitebrowser test.s3db