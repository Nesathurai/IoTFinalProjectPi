from models import Node


class BLE_Filter:
    def __init__(self, thresh: int = -80) -> None:
        """
        The threshold value is set to ignore singals below a certain RSSI.
        With BLE signals below -80 are presumed to be bad.

        The occupation rate is the probability that someone will occupy the room.

        The frequency is the time in minutes in between each scan.
        """
        print(":: INIT FILTER ::")
        self.threshold = thresh
        self.frequency = 45 / 60
        self.occupation_rate = 0.40

    def update_node(self, session, mac: str, devices: list, statics: set):
        """
        Distance / Frequency = # of measurement cycles while distance is traversed.
        # cycles * Ppl per cycle = # people who will check the room before you arrive.
        Probability of a room being taken by a person who sees it empty = 40%
        occupation_rate ^ ppl who will be there before you = Probability the room is occupied.
        Multiply by 5 to translate into five stages [0..4]self.frequency
        """
        print(f":: UPDATE NODE {mac} ::")
        node = session.query(Node).filter_by(id=mac).one()
        print(node)

        addresses = [(dev.split(";")[0], dev.split(";")[1]) for dev in devices if dev]

        print(addresses)
        visitors = [
            dev
            for dev in addresses
            if dev[0] not in statics and int(dev[1]) > self.threshold
        ]
        print(visitors)

        temp_busy = (1 - ((1 - self.occupation_rate) ** len(visitors))) * 5
        freq_ratio = 3 * self.frequency / node.distance
        busyness = (1 - freq_ratio) * node.busyness + freq_ratio * temp_busy
        node.busyness = min(4, busyness)


BLE = BLE_Filter()
