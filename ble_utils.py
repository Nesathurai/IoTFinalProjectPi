import threading
import time

from models import Node


class BLE_Filter:
    def __init__(self, thresh: int = -85) -> None:
        print(":: INIT FILTER ::")
        self.statics = set()
        self.static_timer = 0
        self.threshold = thresh
        self.frequency = 0.5
        self.occupation_rate = 0.40

    def update_node(self, msg, session):
        """
        Distance / Frequency = # of measurement cycles while distance is traversed.
        # cycles * Ppl per cycle = # people who will check the room before you arrive.
        Probability of a room being taken by a person who sees it empty = 40%
        occupation_rate ^ ppl who will be there before you = Probability the room is occupied.
        Multiply by 5 to translate into five stages [0..4]self.frequency
        """
        # node -> mac address
        topic = str(msg.topic)
        split = topic.split("/")
        node = session.query(Node).filter_by(id=split[-1])

        # grab message
        message = msg.payload.decode().split("\n")

        if node.count() == 0:
            # if it does not exist, add to database
            session.add(Node(id=split[0], size="medium", distance=4.0, busyness=0.0))
        # problem here with iterating over mqtt message -> mqtt message object is not iterable

        print(message)
        visitors = [
            dev.split(";")[0]
            for dev in message
            if dev[0] not in self.statics and int(dev[1]) > self.threshold
        ]
        current_busyness = (
            (1 - self.occupation_rate)
            ** (len(visitors) * node.distance / self.frequency)
        ) * 5

        freq_ratio = self.frequency / node.distance
        node.busyness = (1 - freq_ratio) * node.busyness + freq_ratio * current_busyness
        node.busyness = min(4, node.busyness)

    def reset(self, nodes: list):
        print(":: CLEAR STATICS ::")
        self.statics.clear()
        self.static_timer = time.time()
        for node in nodes:
            print(":: LOOPING THROUGH NODES A ::")
            response = node.response
            for ble_device in response:
                self.statics.add(ble_device[0])

        time.sleep(30)

        temp = set()
        for node in nodes:
            print(":: LOOPING THROUGH NODES ::")
            print(node)
            # wait for response from X node
            response = node.response
            for ble_device in response:
                temp.add(ble_device[0])

        self.statics.intersection_update(temp)


BLE = BLE_Filter()
