from sqlalchemy import Column, Integer, String, Float, DateTime, Time
from sqlalchemy.orm import relationship
from models.Database import Base

class Computer(Base):
    __tablename__ = 'computers'

    id = Column(Integer)
    user = relationship('User')

    first_window = Column(String)
    second_window = Column(String)
    third_window = Column(String)
    first_window_percent = Column(Float)
    second_window_percent = Column(Float)
    third_window_percent = Column(Float)

    proc_number = Column(Integer)
    disk_mem_usege = Column(Float)
    CPU_f_min = Column(Float)
    CPU_f_max = Column(Float)
    CPU_f_cur = Column(Float)
    Boot_time = Column(String)
    Total_mem_used = Column(Float)

    date = Column(DateTime)
    time = Column(Time)

    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self) -> str:
        info = f'COMPUTER\n \
                    [ID: {self.id}]\n \
                    [FIRST WINDOW: {self.first_window} ({self.first_window_percent} %)]\n \
                    [SECOND WINDOW: {self.second_window} ({self.second_window_percent} %)]\n \
                    [THIRD WINDOW: {self.third_window} ({self.third_window_percent} %)]\n\n \
                    [PROCESS NUMBER: {self.proc_number}]\n \
                    [DISK MEMORY USAGE: {self.disk_mem_usege}]\n \
                    [CPU FREUENCY (MIN): {self.CPU_f_min}]\n \
                    [CPU FREUENCY (MAX): {self.CPU_f_max}]\n \
                    [CPU FREUENCY (CURRENT): {self.CPU_f_cur}]\n \
                    [BOOT TIME: {self.Boot_time}]\n \
                    [TOTAL MEMORY USED: {self.Total_mem_used}]\n \
                    [DATE: ({self.date}) {self.time}]'