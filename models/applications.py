from datetime import datetime
from xmlrpc.client import DateTime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.Database import Base

class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(32), nullable=True)
    computer = Column(Integer, nullable=True)

    create_time = Column(String)
    status = Column(String(16))
    rss = Column(Integer)
    vms = Column(Integer)
    shared = Column(Integer)
    data = Column(Integer)
    date = Column(DateTime)

    def __init__(self, app_name: str, comp: int):
        self.app_name = app_name
        self.computer = comp

        self.create_time = ''
        self.status = ''
        self.rss = 0
        self.vms = 0
        self.shared = 0
        self.data = 0
        self.date = datetime.now()

    def __repr__(self) -> str:
        return f'Application [ID: {self.id}, Name: {self.app_name}], [TIME: {self.date}]'
    
    def __eq__(self, other_app):
        if isinstance(other_app, Application):
            return (self.app_name == other_app.app_name) and (self.computer == other_app.computer)
        else:
            raise NotImplemented
