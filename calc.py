from typing import List


# calculates the dps from data
def calculateDPS(owner: str, data: List) -> int:
    return sum(int(i["data"]["DPS"]) for i in data if owner == i["owner"])


_demon = ["Demon Queen", "Demon Ace", "Demon King"]
_mecha = ["Mecha Glitter", "Mecha Apollo", "Mecha Draco"]


# calculates the real dps
def calculateItemsDPS(basis: List, data: List, owner: str) -> int:
    dps = 0

    for i in data:
        for k in basis:
            _name = k["data"]["name"].strip()

            if _name in _demon:
                _name = "Demon"
            elif _name in _mecha:
                _name = "Mecha"

            if _name == i["data"]["Item Owner"].strip() and owner == i["owner"]:
                dps += int(i["data"]["DPS"])
                break

    return dps
