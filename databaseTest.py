#https://leportella.com/sqlalchemy-tutorial/
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///database.db', echo=True)
conn = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return f'User {self.name}'

Base.metadata.create_all(engine)
user = User(name='John Snow', password='johnspassword')
session.add(user)

print(user.id)  # None

session.commit()
query = session.query(User).filter_by(name='John Snow')

print(query.count())

session.query(User).filter(User.id == 1).update({'name':"not john snow"})
session.commit()

# trans = conn.begin()
# conn.execute('INSERT INTO "EX1" (name) '
#              'VALUES ("Hello")')
# trans.commit()
