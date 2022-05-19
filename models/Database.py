from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# имя лучше не хранить в коде
DATABASE_NAME = 'worker_base.sqlite'

# такой подход позволяет в любой момент перейти от
# sqlite например к MySQL или к другой СУБД
engine = create_engine(f'sqlite:///{DATABASE_NAME}')

# создает сессию работы с бд
Session = sessionmaker(bind=engine)

# от этой базы будут наследоваться все оздаваемые таблицы
Base = declarative_base()

# прописываем функцию создания БД
def CreateDB():
    Base.metadata.create_all(engine)