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
# def UserMemoryUsedFilter(session: Session, MemoryUsed: float):
#     for it in session.query(User).join(Computer).filter(Computer.Total_mem_used >= MemoryUsed):
#         print(it)

# добавляет нового юзера и компьютер, соответствующий ему
def AddUser(session: Session, name: str, comp: int, ip: str):
    new_user = User(name, comp, ip)
    new_comuter = Computer(comp)
    
    exists_users = session.query(User)
    if new_user in exists_users:
        print("This user already exists")
        raise RuntimeError
    
    exists_computer = session.query(Computer)
    if new_comuter in exists_computer:
        print("This computer already exists")
        raise RuntimeError
    

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
    computer_number_list = [computer.number for computer in session.query(Computer)]
    if comp not in computer_number_list:
        print("You try to add computer without user. This is not you really want)")
        raise RuntimeError

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
def AddApplication(session: Session, app: str, comp: int):
    apps = session.query(Application)
    new_app = Application(app)

    if new_app not in apps:
        session.add(new_app)

        computer = session.query(Computer).filter(Computer.number == comp)
        cur_computer = computer[-1]
        new_app.computers.append(cur_computer)
        session.commit()

    else:
        print('this application is already in database')

'''
выводит время авторизации каждого пользователя
'''
def AuthorisationTime(session: Session):
    users = TakeUsesr(session)

    for user in users:
        first_post = session.query(Computer).join(User).filter(User.name == user).first()
        authorisation_time = first_post.date.strftime("%d-%m-%Y %H:%M:%S")
        print("USER: " + user + " -- AUTHORASION TIME: " + authorisation_time)

'''
выводит время последней активности каждого пользователя
'''
def ExitTime(session: Session):
    users = TakeUsesr(session)

    for user in users:
        computer_date = [computer.date 
                         for computer in 
                         session.query(Computer).join(User).filter(User.name == user)]
        exit_time = computer_date[-1].strftime("%d-%m-%Y %H:%M:%S")
        print("USER: " + user + " -- EXIT TIME: " + exit_time)

'''
функцию возвращает список приложений по имени юзера
'''
def TakeAppsList(session: Session, user_name: str):

    comp = [user.computer for user in session.query(User).filter(User.name == user_name)]

    print("USER: " + user_name + "\nCOMPUTER: %d\n" %comp[0])
    for it, _ in session.query(Application.app_name, Computer.number).filter(and_(
        assotiated_table.c.application_id == Application.id, 
        assotiated_table.c.computer_id == Computer.id, 
        Computer.number == comp[0])):
        print(it)

''' 
по заданному имени пользователя возвращает 2 списка:
первый список (с нулевого индекса) окна первого, второго и третьего приоритета
второй список -- их процентное соотношение по времени
'''
def MostUsasbleWindows(session: Session, user_name: str):
    comp = session.query(Computer).join(User).filter(User.name == user_name)
    cur_comp = comp[-1]

    most_usable_windows = []
    most_usable_windows_persent = []

    most_usable_windows.append(cur_comp.first_window)
    most_usable_windows.append(cur_comp.second_window)
    most_usable_windows.append(cur_comp.third_window)
    most_usable_windows_persent.append(cur_comp.first_window_percent)
    most_usable_windows_persent.append(cur_comp.second_window_percent)
    most_usable_windows_persent.append(cur_comp.third_window_percent)

    return most_usable_windows, most_usable_windows_persent