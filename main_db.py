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

# посмотреть табличку в приложении
#* sqlitebrowser test.s3db