from faker import Faker
from models.Database import CreateDB, Session

from models.applications import Application
from models.user import User
from models.computer import Computer

import DB_access

import datetime

# вызываем функцию создания базы данных с опцией автоматического заполнения
def create_database(load_fake_data: bool = True):
    CreateDB()
    if load_fake_data:
        _load_fake_data(Session())

# низкоуровневая функция, реализующая опцию автоматического заподнения таблицы
def _load_fake_data(session: Session):

    fk = Faker()
    fk = Faker('ru_RU')

    for _ in range(1, 8+1):
        name = fk.name()
        comp = _

        DB_access.AddUser(Session(), name, comp, '')
    
    application_list = ['bash', 'chrom', 'telegram', 'YouTube', 'VScode', 'Tex']
    
    for it in range(1, 8+1):
        info = {
            'first_window' : 'YouTube', 
            'second_window' : 'VK', 
            'third_window' : 'bash', 
            'first_window_percent' : 70, 
            'second_window_percent' : 20, 
            'third_window_percent' : 10, 
            'proc_number' : 200, 
            'disk_mem_usege' : 1.1, 
            'CPU_f_min' : 20, 
            'CPU_f_max' : 20, 
            'CPU_f_cur' : 20, 
            'Boot_time' : 'boot time', 
            'Total_mem_used' : 1.2
        }
        DB_access.AddComputerInfo(Session(), it, info)

    for key, app in enumerate(application_list):
        if key % 2 == 0:
            app_info = {
                'app_name': app,
                'computer': 1,
                'create_time': '01-01-01',
                'status': 'active',
                'rss': 0,
                'vms': 0,
                'shared': 0,
                'data': 0
            }
            DB_access.AddApplication(Session(), app_info)
        if key % 3 == 0:
            app_info = {
                'app_name': app,
                'computer': 2,
                'create_time': '01-01-01',
                'status': 'active',
                'rss': 0,
                'vms': 0,
                'shared': 0,
                'data': 0
            }
            DB_access.AddApplication(Session(), app_info)
        if key % 4 == 0:
            app_info = {
                'app_name': app,
                'computer': 3,
                'create_time': '01-01-01',
                'status': 'active',
                'rss': 0,
                'vms': 0,
                'shared': 0,
                'data': 0
            }
            DB_access.AddApplication(Session(), app_info)
        if key % 5 == 0:
            app_info = {
                'app_name': app,
                'computer': 4,
                'create_time': '01-01-01',
                'status': 'active',
                'rss': 0,
                'vms': 0,
                'shared': 0,
                'data': 0
            }
            DB_access.AddApplication(Session(), app_info)
