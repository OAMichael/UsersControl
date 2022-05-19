from sqlalchemy import Column, Integer, String, Float, DateTime, Time
from sqlalchemy.orm import relationship
from models.Database import Base

class Computer(Base):
    __tablename__ = 'computers'

    id = Column(Integer, primary_key=True)
    user = relationship('User')

    first_window = Column(String)
    second_window = Column(String)
    third_window = Column(String)

    first_window_percent = Column(Float)
    second_window_percent = Column(Float)
    third_window_percent = Column(Float)

    date = Column(DateTime)
    time = Column(Time)

    # по умолчанию
    # def __init__(self):
    
    def __repr__(self) -> str:
        info = f'COMPUTER\n \
                    [ID: {self.id}]\n \
                    [FIRST WINDOW: {self.first_window} ({self.first_window_percent} %)]\n \
                    [SECOND WINDOW: {self.second_window} ({self.second_window_percent} %)]\n \
                    [THIRD WINDOW: {self.third_window} ({self.third_window_percent} %)]\n \
                    [DATE: ({self.date}) {self.time}]'