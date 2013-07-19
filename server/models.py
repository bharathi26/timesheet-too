from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///timesheet.sq3')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    fullname = Column(String)
    password = Column(String)


    def __init__(self, username, fullname, password):
        self.username = username
        self.fullname = fullname
        self.password = password


    def __repr__(self):
        return "<User '{}' '{}'>".format(self.username, self.fullname)


Base.metadata.create_all(engine)
