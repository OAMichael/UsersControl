from sqlalchemy import Column, Integer, String, ForeignKey
from models.Database import Base

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    #TODO: сделать ограничение на длину имени
    #TODO: указать, что это поле не должно быть пустым
    name = Column(String)
    computer = Column(Integer, ForeignKey('Computers.id'))

    def __init__(self, name: str, computer_id: int):
        self.name = name
        self.computer = computer_id

    def __repr__(self) -> str:
        info = f'USER: [NAME: {self.name}] [COMPUTER: {self.computer}]'