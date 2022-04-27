import select
import sys
import time
from datetime import datetime
from turtle import distance

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# https://leportella.com/sqlalchemy-tutorial/
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MQTT_ADDRESS = "10.20.126.8"
MQTT_USER = "cdavid"
MQTT_PASSWORD = "cdavid"
MQTT_TOPIC = "outTopic"

mqtt_client = mqtt.Client()

Base = declarative_base()
engine = create_engine("sqlite:///userDatabase.sqlite", echo=True)
conn = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uid = Column(String)
    name = Column(String)
    access = Column(String)
    lastAccessed = Column(DateTime)

    def __repr__(self):
        return f"User {self.name}"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True)
    size = Column(String)
    distance = Column(Float)
    busyness = Column(Float)

    def __repr__(self):
        return (f"Node: {self.id}\n"
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


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe("#")


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    # https://www.programiz.com/python-programming/datetime/current-datetime
    # setting qos to 1
    if msg.topic.startswith("to/broker"):
        to_broker(msg)
    elif msg.topic.startswith("to/broker/ble"):
        to_ble(msg)
    print()


def to_broker(msg):
    now = datetime.now()
    message = str(msg.payload.decode())
    print(msg.topic + " " + str(msg.payload))

    replyAdd = (
        "Added to database: uid = "
        + message
        + "; name = Allan Nesathurai; access = false ; date_accessed = "
        + now.strftime("%d/%m/%Y %H:%M:%S")
    )

    replyDeny = (
        "User with uid: " + message + " has been denied access. Please try again later."
    )

    replyApproved = "User with uid: " + message + " has been approved access!"

    # check if user in database
    now = datetime.now()
    query = session.query(User).filter_by(uid=message)

    session.commit()
    # if not found, add to database
    if query.count() == 0:
        accept = "False"
        name = "anon"
        print("You have 15 seconds to answer")

        i, o, e = select.select([sys.stdin], [], [], 15)

        if i:
            print("Enter name: ")
            name = sys.stdin.readline().strip()
            print("You said name = ", name)
            print("Enter access: ")
            accept = sys.stdin.readline().strip()
            print("You set access = ", accept)

        else:
            print("You said nothing, using default values")

        # add user; change name later
        user = User(uid=message, name=name, access=accept, lastAccessed=now)
        session.add(user)
        session.commit()
        publish.single(
            "from/broker" + msg.topic.split("/")[2], replyAdd, hostname=MQTT_ADDRESS
        )
        print(replyAdd)
    # now, see if user has access or not
    query = session.query(User).filter_by(uid=message, access="True")
    # user has no access, or not found
    if query.count() == 0:
        publish.single(
            "from/broker" + msg.topic.split("/")[2], replyDeny, hostname=MQTT_ADDRESS
        )
        print(replyDeny)
    else:
        publish.single(
            "from/broker" + msg.topic.split("/")[2],
            replyApproved,
            hostname=MQTT_ADDRESS,
        )
        print(replyDeny)


def to_ble(msg):
    """
    """
    if time.time() - BLE_REFRESH >= (60 * 5):
        BLE_REFRESH = time.time()
        current_devices = set()
        start = time.time()            
        time.sleep(10)
    else:



def on_publish(client, userdata, msg):
    print("Data published")


def main():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(MQTT_ADDRESS, 1883)

    mqtt_client.loop_forever()


if __name__ == "__main__":
    print("MQTT to InfluxDB bridge")
    main()
