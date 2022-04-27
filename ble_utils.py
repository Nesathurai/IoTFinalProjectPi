import threading
import time

# https://leportella.com/sqlalchemy-tutorial/
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///userDatabase.sqlite", echo=True)
conn = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


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


Base.metadata.create_all(engine)

session.add(Node(id="A", size="medium", distance=4.0, busyness=0.0))
session.add(Node(id="B", size="medium", distance=4.12, busyness=0.0))
session.add(Node(id="C", size="medium", distance=4.47, busyness=0.0))
session.add(Node(id="D", size="large", distance=5.0, busyness=0.0))
session.add(Node(id="E", size="medium", distance=4.47, busyness=0.0))
session.add(Node(id="F", size="medium", distance=4.12, busyness=0.0))
session.add(Node(id="G", size="large", distance=4.0, busyness=0.0))

session.commit()


class BLE_Filter:
    def __init__(self, thresh: int = -85) -> None:
        self.statics = set()
        self.static_timer = 0
        self.threshold = thresh
        self.frequency = 0.5
        self.occupation_rate = 0.40

    def update_node(self, msg):
        """
        Distance / Frequency = # of measurement cycles while distance is traversed.
        # cycles * Ppl per cycle = # people who will check the room before you arrive.
        Probability of a room being taken by a person who sees it empty = 40%
        occupation_rate ^ ppl who will be there before you = Probability the room is occupied.
        Multiply by 5 to translate into five stages [0..4]self.frequency
        """
        node: Node = Node.query.filter_by(id=msg.id).all()

        visitors = [
            dev for dev in msg if dev[0] not in self.statics and dev[1] > self.threshold
        ]
        current_busyness = (
            (1 - self.occupation_rate)
            ** (len(visitors) * node.distance / self.frequency)
        ) * 5

        freq_ratio = self.frequency / node.distance
        node.busyness = (1 - freq_ratio) * node.busyness + freq_ratio * current_busyness
        node.busyness = min(4, node.busyness)

    def refresh(self):
        self.statics.clear()
        self.static_timer = time.time()
        for node in Node.query.order_by(Node.id).all():
            response = node.response
            for ble_device in response:
                self.statics.add(ble_device[0])

        time.sleep(30)

        temp = set()
        for node in Node.query.filter(Node.id).all():
            # wait for response from X node
            response = node.response
            for ble_device in response:
                temp.add(ble_device[0])

        self.statics.intersection_update(temp)
