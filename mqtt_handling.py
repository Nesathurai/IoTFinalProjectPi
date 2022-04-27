import select
import sys
from datetime import datetime

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

from models import User
import ble_utils

MQTT_ADDRESS = "10.20.126.8"
MQTT_USER = "cdavid"
MQTT_PASSWORD = "cdavid"
MQTT_TOPIC = "outTopic"

CLIENT = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe("#")


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    if msg.topic.startswith("to/broker/ble"):
        ble_utils.BLE.update_node(msg)
    elif msg.topic.startswith("to/broker"):
        to_broker(msg)


def to_broker(msg, session):
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


def on_publish(client, userdata, msg):
    print("Data published")


def mqtt_init():
    print(":: INIT CLIENT CONNECTION ::")
    CLIENT.on_connect = on_connect
    CLIENT.on_message = on_message
    CLIENT.on_publish = on_publish
    CLIENT.connect(MQTT_ADDRESS, 1883)

    CLIENT.loop_start()


if __name__ == "__main__":
    print("MQTT to InfluxDB bridge")
    mqtt_init()
