from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from models.Database import Base
import datetime

class Computer(Base):
    __slots__ = ['__MachineId'] # инкапсулированное поле
    __tablename__ = 'computers'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=True)
    user = relationship('User')

    first_window = Column(String(32))
    second_window = Column(String(32))
    third_window = Column(String(32))
    first_window_percent = Column(Float)
    second_window_percent = Column(Float)
    third_window_percent = Column(Float)
    curent_window_active = Column(String(32))

    proc_number = Column(Integer)
    disk_mem_usege = Column(Float)
    CPU_f_min = Column(Float)
    CPU_f_max = Column(Float)
    CPU_f_cur = Column(Float)
    Boot_time = Column(String)
    Total_mem_used = Column(Float)

    date = Column(DateTime)

    def __init__(self, MachineID: str, number: int):
        self.__MachineId = MachineID
        self.number = number
        self.first_window = ''
        self.second_window = ''
        self.third_window = ''
        self.first_window_percent = 0
        self.second_window_percent = 0
        self.third_window_percent = 0
        self.curent_window_active = ''

        self.proc_number = 0
        self.disk_mem_usege = 0
        self.CPU_f_min = 0
        self.CPU_f_max = 0
        self.CPU_f_cur = 0
        self.Boot_time = ''
        self.Total_mem_used = 0

        self.date = datetime.datetime.now()

    # на всякий случай, чтобы разработчик мог извлечь значение из кода
    @property # <- применяется для гетеров   
    def MachineId(self):
        return self.__MachineId
    
    def __repr__(self) -> str:
        info = f'COMPUTER\n \
                    [ID: {self.id}]\n \
                    [NUMBER: {self.number}]\n \
                    [FIRST WINDOW: {self.first_window} ({self.first_window_percent} %)]\n \
                    [SECOND WINDOW: {self.second_window} ({self.second_window_percent} %)]\n \
                    [THIRD WINDOW: {self.third_window} ({self.third_window_percent} %)]\n \
                    [CURRENT ACTIVE WINDOW: {self.curent_window_active}]\n\n \
                    [PROCESS NUMBER: {self.proc_number}]\n \
                    [DISK MEMORY USAGE: {self.disk_mem_usege}]\n \
                    [CPU FREUENCY (MIN): {self.CPU_f_min}]\n \
                    [CPU FREUENCY (MAX): {self.CPU_f_max}]\n \
                    [CPU FREUENCY (CURRENT): {self.CPU_f_cur}]\n \
                    [BOOT TIME: {self.Boot_time}]\n \
                    [TOTAL MEMORY USED: {self.Total_mem_used}]\n \
                    [DATE: {self.date.strftime("%d-%m-%Y %H-%M")}]'
        return info
    
    def __eq__(self, other):
        if isinstance(other, Computer):
            return self.number == other.number
        else:
            raise NotImplemented