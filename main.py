import os
from fastapi import FastAPI, Response, status
from deta import Deta


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