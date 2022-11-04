from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td

def callbackFunc(s):
    print(s)

if __name__ == "__main__":
    pair = "ES"
    market = "futures"
    username = None
    password = None
    trading = td.TradingViewWs(pair, market, username, password)
    trading.realtime_quote(callbackFunc)
