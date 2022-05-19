from faker import Faker
from models import student
from models.Database import CreateDB, Session

from models.User import User
from models.Computer import Computer

# вызываем функцию создания базы данных с опцией автоматического заполнения
def create_database(load_fake_data: bool = True):
    CreateDB()
    if load_fake_data:
        _load_fake_data(Session())

# низкоуровневая функция, реализующая опцию автоматического заподнения таблицы
def _load_fake_data(session: Session):
    ...
