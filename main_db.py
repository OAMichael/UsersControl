#!/usr/bin/python3

import os
from tkinter import SE
from models.Database import DATABASE_NAME
from models.Database import Session
import CreateDB as db_creator

from datetime import datetime

import DB_access

if __name__ == '__main__':
    
    db_existed = os.path.exists(DATABASE_NAME)
    if not db_existed:
        db_creator.create_database()

    DB_access.AddUser(Session(), 'Pavel', 10)

# посмотреть табличку в приложении
#* sqlitebrowser test.s3db