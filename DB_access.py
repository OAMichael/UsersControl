from requests import session
from sqlalchemy import and_
from models.Database import Session
from models.applications import Application, assotiated_table
from models.user import User
from models.computer import Computer

# дает полную информацию о компьютере по имени пользователя
def PrintComputerInfo(session: Session, name: str):
    for it in session.query(Computer).join(User).filter(User.name == name):
        print(it)

# выводит список всех пользователей, чей Total_mem_used превышает заданное значение
def UserMemoryUsedFilter(session: Session, MemoryUsed: float):
    for it in session.query(User).join(Computer).filter(Computer.Total_mem_used >= MemoryUsed):
        print(it)

# добавляет нового юзера и компьютер, соответствующий ему
def AddUser(session: Session, name: str, comp: int):
    new_user = User(name, comp)
    new_comuter = Computer(comp)
    
    exists_users = session.query(User)
    if new_user in exists_users:
        print("This user already exists")
        return
    
    exists_computer = session.query(Computer)
    if new_comuter in exists_computer:
        print("This computer already exists")
        return
    

    session.add(new_user)
    session.add(new_comuter)
    session.commit()
    session.close()

# возвращает текущий список пользователей
def TakeUsesr(session: Session):
    users = session.query(User)
    users_names = [user.name for user in users]
    return users_names

'''
дообавляем запись о компьютере под номером comp
информация передается в кортеже, который имеет следующую стуктуру

название окна первого приоритета (str)
название окна второго приоритета (str)
название окна третьего приоритета (str)
процент, занимаемый окном первого приоритета (float)
процент, занимаемый окном второго приоритета (float)
процент, занимаемый окном третьего приоритета (float)
количество процессов (int)
disk memory used (float)
CPU frequency min (float)
CPU frequency max (float)
CPU frequency current (float)
Boot time (str)
Total memory used (float)
Текущая дата и время (указывается через datetime.datetime.now())

Пример:
info = ('YouTube', 'VK', 'bash', 70, 20, 10, 200, 1.1, 20, 20, 20, 'boot time', 1.2, datetime.datetime.now())
'''
def AddComputerInfo(session: Session, comp: int, info: tuple):
    computer = Computer(comp)
    computer.first_window = info[0]
    computer.second_window = info[1]
    computer.third_window = info[2]

    computer.first_window_percent = info[3]
    computer.second_window_percent = info[4]
    computer.third_window_percent = info[5]

    computer.proc_number = info[6]

    computer.disk_mem_usege = info[7]

    computer.CPU_f_min = info[8]
    computer.CPU_f_max = info[9]
    computer.CPU_f_cur = info[10]
    computer.Boot_time = info[11]
    computer.Total_mem_used = info[12]
    computer.date = info[13]

    session.add(computer)
    session.commit()
    session.close()

'''
Добавляет новое приложение в таблицу приложений, если его там не было
'''
def AddApplication(session: Session, app: str):
    apps = session.query(Application)
    new_app = Application(app)

    if new_app not in apps:
        session.add(new_app)

        computers = session.query(Computer)

        for comp in computers:
            cur_comp = Assosiation(new_app, comp)
            if cur_comp != None:
                new_app.computers.append(comp)
                session.commit()

    else:
        print('this application is already in database')

# проводит ассоциацию между списком приложений и компьютерами, которые когда-либо его использвали
def Assosiation(app: Application, comp: Computer):
    if (comp.first_window == app.app_name or 
        comp.second_window == app.app_name or 
        comp.third_window == app.app_name):
        # app.computers.append(comp)
        return comp
    else:
        return None

