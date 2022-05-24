from sqlalchemy import Column, Integer, String, ForeignKey
from models.Database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=True)
    computer = Column(Integer, ForeignKey('computers.number'), nullable=True)
    ip_addr = Column(String(len('000.000.0.000')))

    def __init__(self, name: str, computer_id: int, ip_addr = ''):
        self.name = name
        self.computer = computer_id
        self.ip_addr = ip_addr

    def __repr__(self) -> str:
        info = f'USER: [NAME: {self.name}] [COMPUTER: {self.computer}] [IP: {self.ip_addr}]'
        return info

    def __eq__(self, other):
        if isinstance(other, User):
            return self.name == other.name
        else:
            raise NotImplemented