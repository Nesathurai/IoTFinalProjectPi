import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Decentralized RFID Tracking and Occupancy Control Using ESP32s")

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

        self.after(1000, lambda: self.update_node("D"))
        self.after(1000, lambda: self.update_node("G"))

    def resize_image(self, img: str, ratio: float = 0.14):
        medium_room = Image.open(img)
        width, height = int(medium_room.width * ratio), int(medium_room.height * ratio)
        self.image = medium_room.resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(self.image)

    def update_node(self, node: str):
        self.nodes[node][0] = (self.nodes[node][0] + 1) % 6
        img = self.resize_image(f"./images/large_room_{self.nodes[node][0]}.png", 0.37)
        self.nodes[node][1].configure(image=img)
        self.nodes[node][1].image = img
        self.after(250, lambda: self.update_node(node))


if __name__ == "__main__":
    app = App()
    app.mainloop()