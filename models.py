from sqlalchemy import Column, Float, Integer, String, DateTime

from db import Base, Session, engine


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True)
    size = Column(String)
    distance = Column(Float)
    busyness = Column(Float)

    def __repr__(self):
        return (
            f"Node: {self.id}\n"
            f"Size: {self.size}\n"
            f"Distance (min): {self.distance}\n"
            f"Busyness (ppl/min): {self.busyness}"
        )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uid = Column(String)
    name = Column(String)
    access = Column(String)
    lastAccessed = Column(DateTime)

    def __repr__(self):
        return f"User {self.name}"


Base.metadata.create_all(engine)
