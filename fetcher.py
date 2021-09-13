import requests
import os


def _fetcher(url: str):
    try:
        # os.environ will cause an error which we want
        r = requests.get(url)

        print(r.headers)
        return r.json()

    except Exception as e:
        print(e)
        _fetcher(url)


# dps getter
def fetcher_worker(wallet: str):
    return _fetcher(os.environ["FETCHER_API"] + f"fetchall/{wallet}")


# season one pass getter
def seasonfetcher_worker(wallet: str):
    return _fetcher(os.environ["FETCHER_API"] + f"seasonpass/one?wallet={wallet}")
