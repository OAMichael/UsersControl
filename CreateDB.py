from faker import Faker
from models.Database import CreateDB, Session

from models.applications import Application
from models.user import User
from models.computer import Computer

import datetime

# вызываем функцию создания базы данных с опцией автоматического заполнения
def create_database(load_fake_data: bool = True):
    CreateDB()
    if load_fake_data:
        _load_fake_data(Session())

# низкоуровневая функция, реализующая опцию автоматического заподнения таблицы
def _load_fake_data(session: Session):
    computer1 = Computer(1)
    computer2 = Computer(2)
    computer3 = Computer(3)
    computer4 = Computer(4)
    computer5 = Computer(5)
    computer6 = Computer(6)
    computer7 = Computer(7)
    computer8 = Computer(8)

    session.add(computer1)
    session.add(computer2)
    session.add(computer3)
    session.add(computer4)
    session.add(computer5)
    session.add(computer6)
    session.add(computer7)
    session.add(computer8)
    
    application_list = ['bash', 'chrom', 'telegram', 'YouTube', 'VScode', 'Tex']

    for key, app in enumerate(application_list):
        application = Application(app)

        if key % 2 == 0:
            application.computers.append(computer1)
        if key % 3 == 0:
            application.computers.append(computer2)
        if key % 4 == 0:
            application.computers.append(computer3)
        if key % 5 == 0:
            application.computers.append(computer4)

    session.commit()

    fk = Faker()
    fk = Faker('ru_RU')
    computer_list = [computer1, computer2, computer3, computer4, computer5, computer6, computer7, computer8]
    
    for key, comp in enumerate(computer_list):
        comp.first_window = "YouTube"
        comp.second_window = "YouTube"
        comp.third_window = "YouTube"

        comp.first_window_percent = 100
        comp.second_window_percent = 100
        comp.third_window_percent = 100

        comp.proc_number = 50
        comp.disk_mem_usege = 20
        comp.CPU_f_min = 500
        comp.CPU_f_max = 500
        comp.CPU_f_cur = 500
        comp.Boot_time = "01-01-01"
        comp.Total_mem_used = 1.1

        comp.date = datetime.datetime.now()

    for _ in range(1, 8+1):
        name = fk.name()
        comp = _

        user = User(name, comp)
        session.add(user)
    
    session.commit()
    session.close()
