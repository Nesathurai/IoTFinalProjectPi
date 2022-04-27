import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import mqtt_handling
import ble_utils

from db import Session, engine
from models import Node

session = Session()

if session.query(Node).filter_by(id="A").first():
    session.add(Node(id="A", size="medium", distance=4.0, busyness=0.0))
if session.query(Node).filter_by(id="B").first():
    session.add(Node(id="B", size="medium", distance=4.12, busyness=0.0))
if session.query(Node).filter_by(id="C").first():
    session.add(Node(id="C", size="medium", distance=4.47, busyness=0.0))
if session.query(Node).filter_by(id="D").first():
    session.add(Node(id="D", size="large", distance=5.0, busyness=0.0))
if session.query(Node).filter_by(id="E").first():
    session.add(Node(id="E", size="medium", distance=4.47, busyness=0.0))
if session.query(Node).filter_by(id="F").first():
    session.add(Node(id="F", size="medium", distance=4.12, busyness=0.0))
if session.query(Node).filter_by(id="G").first():
    session.add(Node(id="G", size="large", distance=4.0, busyness=0.0))

session.commit()


class App(tk.Tk):
    def __init__(self, controller=None, *args, **kwargs):
        print(":: INIT APP ::")
        super().__init__(*args, **kwargs)
        self.title("Decentralized RFID Tracking and Occupancy Control Using ESP32s")

        #mqtt_handling.mqtt_init()

        self.nodes = {
            "A": [0, None],
            "B": [0, None],
            "C": [0, None],
            "D": [0, None],
            "E": [0, None],
            "F": [0, None],
            "G": [0, None],
        }
        medium = self.resize_image("./images/medium_room_0.png")
        large = self.resize_image("./images/large_room_0.png", 0.37)
        YAH = self.resize_image("./images/here.png", 0.25)

        self.nodes["A"][1] = ttk.Label(self, image=medium)
        self.nodes["A"][1].image = medium
        self.nodes["A"][1].grid(row=0, column=0, sticky="e")

        self.nodes["B"][1] = ttk.Label(self, image=medium)
        self.nodes["B"][1].image = medium
        self.nodes["B"][1].grid(row=0, column=1, sticky="e")

        self.nodes["C"][1] = ttk.Label(self, image=medium)
        self.nodes["C"][1].image = medium
        self.nodes["C"][1].grid(row=0, column=2, sticky="e")

        self.nodes["D"][1] = ttk.Label(self, image=large)
        self.nodes["D"][1].image = large
        self.nodes["D"][1].grid(row=0, column=3, sticky="e")

        self.nodes["E"][1] = ttk.Label(self, image=medium)
        self.nodes["E"][1].image = medium
        self.nodes["E"][1].grid(row=1, column=3, sticky="e")

        self.nodes["F"][1] = ttk.Label(self, image=medium)
        self.nodes["F"][1].image = medium
        self.nodes["F"][1].grid(row=2, column=3, sticky="e")

        self.nodes["G"][1] = ttk.Label(self, image=large)
        self.nodes["G"][1].image = large
        self.nodes["G"][1].grid(row=3, column=3, sticky="e")

        self.nodes["You Are Here"] = ttk.Label(self, image=YAH)
        self.nodes["You Are Here"].image = YAH
        self.nodes["You Are Here"].grid(row=3, column=0)

        self.after(2500, lambda: self.update_med_node("A"))
        self.after(2500, lambda: self.update_med_node("B"))
        self.after(2500, lambda: self.update_med_node("C"))
        self.after(2500, lambda: self.update_large_node("D"))
        self.after(2500, lambda: self.update_med_node("E"))
        self.after(2500, lambda: self.update_med_node("F"))
        self.after(2500, lambda: self.update_large_node("G"))
        
        print(":: INIT BLE STATICS ::")
        #self.after(10 * 60, self.reset_ble)

    def resize_image(self, img: str, ratio: float = 0.14):
        medium_room = Image.open(img)
        width, height = int(medium_room.width * ratio), int(medium_room.height * ratio)
        self.image = medium_room.resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(self.image)

    def update_med_node(self, node: str):
        self.nodes[node][0] = (self.nodes[node][0] + 1) % 5
        img = self.resize_image(f"./images/medium_room_{self.nodes[node][0]}.png", 0.14)
        self.nodes[node][1].configure(image=img)
        self.nodes[node][1].image = img
        self.after(2500, lambda: self.update_med_node(node))

    def update_large_node(self, node: str):
        self.nodes[node][0] = (self.nodes[node][0] + 1) % 5
        img = self.resize_image(f"./images/large_room_{self.nodes[node][0]}.png", 0.37)
        self.nodes[node][1].configure(image=img)
        self.nodes[node][1].image = img
        self.after(2500, lambda: self.update_large_node(node))

    def reset_ble(self):
        ble_utils.BLE.reset(session.query(Node).all())
        self.after(10 * 60, self.reset_ble)


if __name__ == "__main__":
    app = App()
    app.mainloop()
