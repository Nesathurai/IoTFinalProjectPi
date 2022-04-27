from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
