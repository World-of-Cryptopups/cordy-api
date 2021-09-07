from calc import calculateDPS, calculateItemsDPS
from fetcher import fetcher_worker, seasonfetcher_worker
import os
from fastapi import FastAPI, Response, status
from deta import Deta
from pydantic import BaseModel


app = FastAPI()
deta = Deta(os.getenv("DETA_PROJECT_KEY"))

# dps db
dpsDB = deta.Base("DPSInfos")
# main db
wocDB = deta.Base("WoC_DATA")


@app.get("/")
async def index():
    return "Hello World"


# fetch user info
@app.get("/id/{userid}")
async def userid(userid: str, res: Response):
    user = wocDB.get(userid)

    if user is None:
        res.status_code = status.HTTP_404_NOT_FOUND

    return {
        "success": user is not None,
        "data": user,
        "message": "User does not exist!" if user is None else "",
    }


# get user current dps data
@app.get("/dps/{userid}")
async def userdps(userid: str, res: Response):
    userDPS = dpsDB.get(userid)

    if userDPS is None:
        res.status_code = status.HTTP_404_NOT_FOUND

    return {
        "success": userDPS is not None,
        "data": userDPS,
        "message": "User does not exist!" if userDPS is None else "",
    }


class DpsCalculator(BaseModel):
    id: str
    username: str
    avatar: str
    tag: str


# dps fetcher and calculator
@app.post("/dps/calculator/{wallet}")
async def dpsCalculator(body: DpsCalculator, wallet: str):
    data = fetcher_worker(wallet)

    pupskinsDPS = calculateDPS(wallet, data["data"]["pupskins"])
    pupcardsDPS = calculateDPS(wallet, data["data"]["pupcards"])
    pupitemsDPSRaw = calculateDPS(wallet, data["data"]["pupitems"])
    pupitemsDPSReal = calculateItemsDPS(
        data["data"]["pupskins"], data["data"]["pupitems"], wallet
    )

    x = {
        "wallet": wallet,
        "user": {
            "id": body.id,
            "username": body.username,
            "avatar": body.avatar,
            "tag": body.tag,
        },
        "dps": {
            "pupskins": pupskinsDPS,
            "pupcards": pupcardsDPS,
            "pupitems": {"raw": pupitemsDPSRaw, "real": pupitemsDPSReal},
        },
    }

    dpsDB.put(x, body.id)

    return {"success": True, "data": x, "message": ""}


# seasonpass getter
@app.get("/seasonpass/one/{wallet}")
async def seasonOnePass(wallet: str):
    data = seasonfetcher_worker(wallet)

    pupskinsDPS = calculateDPS(wallet, data["pupskins"])
    pupcardsDPS = calculateDPS(wallet, data["pupcards"])
    pupitemsDPSRaw = calculateDPS(wallet, data["pupitems"])
    pupitemsDPSReal = calculateItemsDPS(data["pupskins"], data["pupitems"], wallet)

    return {
        "success": True,
        "data": {
            "wallet": wallet,
            "season": "one",
            "dps": {
                "pupskins": pupskinsDPS,
                "pupcards": pupcardsDPS,
                "pupitems": {"raw": pupitemsDPSRaw, "real": pupitemsDPSReal},
            },
        },
        "message": "",
    }
