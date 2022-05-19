from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.Database import Base

# вспомогательная таблица, которая используется для определения связей "Многие ко многим"
assotiated_table = Table('assotioation', Base.metadata,
                                         Column('application_id', Integer, ForeignKey('applications.id')),
                                         Column('computer_id', Integer, ForeignKey('computers.number'))
                                         )

class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    app_name = Column(String)

    computers = relationship('Computer', secondary=assotiated_table, backref='group_lesson')

    def __init__(self, app_name: str):
        self.app_name = app_name

    def __repr__(self) -> str:
        return f'Application [ID: {self.id}, Name: {self.app_name}]'
