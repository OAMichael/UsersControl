#!/usr/bin/python3

import os
from tkinter import SE
from models.Database import DATABASE_NAME
from models.Database import Session
import CreateDB as db_creator

import datetime

import DB_access

if __name__ == '__main__':
    
    db_existed = os.path.exists(DATABASE_NAME)
    if not db_existed:
        db_creator.create_database()

    # info = ('YouTube', 'VK', 'PornHub', 70, 20, 10, 200, 1.1, 20, 20, 20, 'boot time', 1.2, datetime.datetime.now())
    # DB_access.AddComputerInfo(Session(), 4, info)

    # DB_access.AddApplication(Session(), 'PornHub')

    print(DB_access.TakeUsesr(Session()))

# посмотреть табличку в приложении
#* sqlitebrowser test.s3db