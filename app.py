import select
import sys
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import paho.mqtt.client as mqtt
from paho.mqtt import publish
from PIL import Image, ImageTk

import ble_utils
from db import Session
from models import Node, User

MQTT_ADDRESS = "10.20.126.8"
MQTT_USER = "cdavid"
MQTT_PASSWORD = "cdavid"
MQTT_TOPIC = "outTopic"

CLIENT = mqtt.Client()

session = Session()

if not session.query(Node).filter_by(id="40:91:51:9A:A5:DC").first():
    session.add(
        Node(id="40:91:51:9A:A5:DC", size="medium", distance=4.00, busyness=0.0)
    )
if not session.query(Node).filter_by(id="30:C6:F7:03:68:38").first():
    session.add(
        Node(id="30:C6:F7:03:68:38", size="medium", distance=4.12, busyness=0.0)
    )
if not session.query(Node).filter_by(id="40:91:51:BE:F5:D4").first():
    session.add(
        Node(id="40:91:51:BE:F5:D4", size="medium", distance=4.47, busyness=0.0)
    )
if not session.query(Node).filter_by(id="30:C6:F7:03:79:30").first():
    session.add(
        Node(id="30:C6:F7:03:79:30", size="large", distance=5.00, busyness=0.00)
    )
if not session.query(Node).filter_by(id="E").first():
    session.add(Node(id="E", size="medium", distance=4.47, busyness=0.0))
if not session.query(Node).filter_by(id="F").first():
    session.add(Node(id="F", size="medium", distance=4.12, busyness=0.0))
if not session.query(Node).filter_by(id="G").first():
    session.add(Node(id="G", size="large", distance=4.0, busyness=0.0))

session.commit()

NODES = {
    "40:91:51:9A:A5:DC": [None, set(), False, ""],
    "30:C6:F7:03:68:38": [None, set(), False, ""],
    "40:91:51:BE:F5:D4": [None, set(), False, ""],
    "30:C6:F7:03:79:30": [None, set(), False, ""],
    "E": [None, set(), False, ""],
    "F": [None, set(), False, ""],
    "G": [None, set(), False, ""],
}


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        """Initialization for TKinter GUI.

        NODES:
            Dictionary of all nodes in the system. The key is the MAC, and the value is
            the image for the GUI, a set of the static devices found, and whether that
            set of static devices should be reinitialized.
        """
        print(":: INIT APP ::")
        super().__init__(*args, **kwargs)
        self.title("Decentralized RFID Tracking and Occupancy Control Using ESP32s")

        mqtt_init()

        medium = self.resize_image("./images/medium_room_0.png")
        large = self.resize_image("./images/large_room_0.png", 0.37)
        YAH = self.resize_image("./images/here.png", 0.25)

        NODES["40:91:51:9A:A5:DC"][0] = ttk.Label(
            self,
            image=medium,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["40:91:51:9A:A5:DC"][0].image = medium
        NODES["40:91:51:9A:A5:DC"][0].grid(row=0, column=0, sticky="e")

        NODES["30:C6:F7:03:68:38"][0] = ttk.Label(
            self,
            image=medium,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["30:C6:F7:03:68:38"][0].image = medium
        NODES["30:C6:F7:03:68:38"][0].grid(row=0, column=1, sticky="e")

        NODES["40:91:51:BE:F5:D4"][0] = ttk.Label(
            self,
            image=medium,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["40:91:51:BE:F5:D4"][0].image = medium
        NODES["40:91:51:BE:F5:D4"][0].grid(row=0, column=2, sticky="e")

        NODES["30:C6:F7:03:79:30"][0] = ttk.Label(
            self,
            image=large,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["30:C6:F7:03:79:30"][0].image = large
        NODES["30:C6:F7:03:79:30"][0].grid(row=0, column=3, sticky="e")

        NODES["E"][0] = ttk.Label(
            self,
            image=medium,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["E"][0].image = medium
        NODES["E"][0].grid(row=1, column=3, sticky="e")

        NODES["F"][0] = ttk.Label(
            self,
            image=medium,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["F"][0].image = medium
        NODES["F"][0].grid(row=2, column=3, sticky="e")

        NODES["G"][0] = ttk.Label(
            self,
            image=large,
            text="AVAILABLE",
            compound="center",
            font=("consolas", 25),
        )
        NODES["G"][0].image = large
        NODES["G"][0].grid(row=3, column=3, sticky="e")

        self.yah = ttk.Label(self, image=YAH)
        self.yah.image = YAH
        self.yah.grid(row=3, column=0)

        self.after(2500, lambda: self.update_med_node("40:91:51:9A:A5:DC"))
        self.after(2500, lambda: self.update_med_node("30:C6:F7:03:68:38"))
        self.after(2500, lambda: self.update_med_node("40:91:51:BE:F5:D4"))
        self.after(2500, lambda: self.update_large_node("30:C6:F7:03:79:30"))
        self.after(2500, lambda: self.update_med_node("E"))
        self.after(2500, lambda: self.update_med_node("F"))
        self.after(2500, lambda: self.update_large_node("G"))

        self.after(10000, self.reset_ble)

    def resize_image(self, img: str, ratio: float = 0.14):
        medium_room = Image.open(img)
        width, height = int(medium_room.width * ratio), int(medium_room.height * ratio)
        self.image = medium_room.resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(self.image)

    def update_med_node(self, mac: str):
        node = session.query(Node).filter_by(id=mac).one()
        img = self.resize_image(
            f"./images/medium_room_{node.busyness % 5:.0f}.png", 0.14
        )
        NODES[mac][0].configure(image=img)
        NODES[mac][0].image = img
        self.after(2500, lambda: self.update_med_node(mac))

    def update_large_node(self, mac: str):
        node = session.query(Node).filter_by(id=mac).one()
        img = self.resize_image(
            f"./images/large_room_{node.busyness % 5:.0f}.png", 0.37
        )
        NODES[mac][0].configure(image=img)
        NODES[mac][0].image = img
        self.after(2500, lambda: self.update_large_node(mac))

    def reset_ble(self):
        print(":: RESETTING STATICS ::")
        for n, _ in NODES.items():
            NODES[n][2] = True
        self.after(5 * 1000 * 60, self.reset_ble)


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server."""
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe("#")


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    if msg.topic.startswith("to/broker/BLE"):
        mac = str(msg.topic).split("/")[-1]
        devices = [dev for dev in msg.payload.decode().split("\n") if dev]

        if NODES[mac][2]:
            print(f"\n:: STATICS FOR NODE {mac} ::")
            NODES[mac][1] = [dev.split(";")[0] for dev in devices]
            NODES[mac][2] = False
            print(NODES[mac][1])
        else:
            ble_utils.BLE.update_node(session, mac, devices, NODES[mac][1])

    elif msg.topic.startswith("to/broker"):
        to_broker(msg)

    session.commit()


def to_broker(msg):
    now = datetime.now()
    uid = msg.payload.decode()

    print()
    print(msg.topic + " " + msg.payload.decode())

    replyAdd = "Added to database: uid = " + uid + now.strftime("%d/%m/%Y %H:%M:%S")

    replyDeny = (
        "User with uid: " + uid + " has been denied access. Please try again later."
    )

    replyApproved = "User with uid: " + uid + " has been approved access!"
    replyFreed = "User with uid: " + uid + " has exited room."

    # check if user in database
    now = datetime.now()
    query = session.query(User).filter_by(uid=uid)
    mac = msg.topic.split("/")[-1]

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
        user = User(uid=uid, name=name, access=accept, lastAccessed=now)
        session.add(user)
        session.commit()
        publish.single("from/broker" + mac, replyAdd, hostname=MQTT_ADDRESS)
        print(replyAdd)

    # now, see if user has access or not
    query = session.query(User).filter_by(uid=uid, access="True")

    # user has no access, or not found
    if query.count() and NODES[mac][0].cget("text") == "AVAILABLE":
        NODES[mac][0].configure(text="OCCUPIED")
        NODES[mac][3] = uid
        publish.single(
            "from/broker" + mac,
            replyApproved,
            hostname=MQTT_ADDRESS,
        )
        print(replyApproved)
    elif query.count() and NODES[mac][3] == uid:
        NODES[mac][0].configure(text="AVAILABLE")
        publish.single("from/broker" + mac, replyFreed, hostname=MQTT_ADDRESS)
        print(replyFreed)
    else:
        publish.single("from/broker" + mac, replyDeny, hostname=MQTT_ADDRESS)
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
    app = App()
    app.mainloop()
