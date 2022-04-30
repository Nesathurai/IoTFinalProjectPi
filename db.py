from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine("sqlite:///database.db", connect_args={'check_same_thread': False})
conn = engine.connect()
Session = sessionmaker(bind=engine)
