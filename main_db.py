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
        db_creator.create_database(False)

    '''Your code here'''

    # DB_access.AddUser(Session(), 'Pavel', 5)
    # DB_access.AddUser(Session(), 'Misha', 25)
    # DB_access.AddUser(Session(), 'Pavel', 3)
    # DB_access.AddUser(Session(), 'Dima', 25)

    # # DB_access.PrintComputerInfo(Session(), 'Pavel')
    info = ('YouTube', 'VK', 'bash', 70, 20, 10, 200, 1.1, 20, 20, 20, 'boot time', 1.2, datetime.datetime.now())
    # DB_access.AddComputerInfo(Session(), 5, info)
    # DB_access.AddComputerInfo(Session(), 5, info)

    # DB_access.AddUser(Session(), 'Gena', 0)
    # DB_access.AuthorisationTime(Session())
    DB_access.AddComputerInfo(Session(), 111, info)

# посмотреть табличку в приложении
#* sqlitebrowser test.s3db