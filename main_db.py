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

    DB_access.PrintComputerInfo(Session(), 'Калашникова Лариса Семеновна')
    print('*' * 100)
    for it in DB_access.TakeUsesr(Session()):
        print(it)
    print('*' * 100)
    DB_access.AuthorisationTime(Session())
    print('*' * 100)
    DB_access.ExitTime(Session())
    print('*' * 100)
    DB_access.TakeAppsList(Session(), 'Савин Григорий Еремеевич')


# посмотреть табличку в приложении
#* sqlitebrowser test.s3db