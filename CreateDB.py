from faker import Faker
from models.Database import CreateDB, Session

from models.applications import Application
from models.user import User
from models.computer import Computer

# вызываем функцию создания базы данных с опцией автоматического заполнения
def create_database(load_fake_data: bool = True):
    CreateDB()
    if load_fake_data:
        _load_fake_data(Session())

# низкоуровневая функция, реализующая опцию автоматического заподнения таблицы
def _load_fake_data(session: Session):
    ...
