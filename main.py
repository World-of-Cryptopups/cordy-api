from typing import Dict, List
from calc import calculateDPS, calculateItemsDPS
from fetcher import fetcher_worker, seasonfetcher_worker
import os
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from deta import Deta
from pydantic import BaseModel


# new fastapi app
app = FastAPI()

# add cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# new deta project
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


# demand get the dps of the user and update
@app.get("/dps/demand/{userid}")
async def dpsDemanCalculator(userid: str, res: Response):
    user = wocDB.get(userid)

    if user is None:
        res.status_code = status.HTTP_404_NOT_FOUND

        return {"success": False, "data": None, "message": "User does not exist!"}

    wallet = user["wallet"]

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
            "id": user["user"]["id"],
            "username": user["user"]["username"],
            "avatar": user["user"]["avatar"],
            "tag": user["user"]["tag"],
        },
        "dps": {
            "pupskins": pupskinsDPS,
            "pupcards": pupcardsDPS,
            "pupitems": {"raw": pupitemsDPSRaw, "real": pupitemsDPSReal},
        },
    }

    dpsDB.put(x, user["user"]["id"])

    return {"success": True, "data": x, "message": ""}


# calculate dps object
def calcDPS(i: Dict):
    return (
        i["dps"]["pupcards"]
        + i["dps"]["pupskins"]
        + i["dps"]["pupitems"]["raw"]
        + i["dps"]["pupitems"]["real"]
    )


# get all items and sort to get the leaderboard
@app.get("/leaderboard")
async def leaderboard():
    try:
        q = dpsDB.fetch()
        allitems: List[Dict] = q.items

        while q.last:
            allitems += q.items

    except Exception as e:
        return {"success": False, "data": None, "message": e}

    allitems.sort(
        key=lambda i: calcDPS(i),
        reverse=True,
    )

    return {"success": True, "data": allitems, "message": ""}
