from twstock.stock import Stock as BaseStock
from twstock.stock import TWSEFetcher, TPEXFetcher
from twstock.codes import codes

class CustomStock(BaseStock):
    def __init__(self, sid: str, initial_fetch: bool=True):
        self.sid = sid
        # 修改 fetcher 的分配邏輯
        if codes[sid].market in ('上市', '上市臺灣創新板'):
            self.fetcher = TWSEFetcher()
        else:
            self.fetcher = TPEXFetcher()

        self.raw_data = []
        self.data = []

        # Init data
        if initial_fetch:
            self.fetch_31()

