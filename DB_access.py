from requests import session
from sqlalchemy import and_
from models.Database import Session
from models.applications import Application, assotiated_table
from models.user import User
from models.computer import Computer

# def Date(date) -> list:
#     a = date.strftime("%Y %m %d %H %M %S").split()
#     result = [int(item) for item in a]

#     return result


# дает полную информацию о компьютере по имени пользователя
def PrintComputerInfo(session: Session, name: str):
    for it in session.query(Computer).join(User).filter(User.name == name):
        print(it)

# выводит список всех пользователей, чей Total_mem_used превышает заданное значение
def UserMemoryUsedFilter(session: Session, MemoryUsed: float):
    for it in session.query(User).join(Computer).filter(Computer.Total_mem_used >= MemoryUsed):
        print(it)

def AddUser(session: Session, name: str, comp: int):
    user = User(name, comp)
    comuter = Computer(comp)

    session.add(user)
    session.add(comuter)
    session.commit()
    session.close()

def AddComputerInfo(session: Session, comp: int):
    ...

def AddApplication(session: Session, app: str):
    ...

def Assosiation(session: Session, app: str, comp: int):
    ...
