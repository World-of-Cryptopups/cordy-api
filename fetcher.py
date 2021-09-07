import requests
import os


def _fetcher(url: str):
    try:
        # os.environ will cause an error which we want
        r = requests.get(url)

        return r.json()
    except KeyError:
        pass
    except Exception:
        _fetcher(url)


# dps getter
def fetcher_worker(wallet: str):
    return _fetcher(os.environ["FETCHER_API"] + f"fetchall/{wallet}")


# season one pass getter
def seasonfetcher_worker(wallet: str):
    return _fetcher(os.environ["FETCHER_API"] + f"seasonpass/one?wallet={wallet}")
