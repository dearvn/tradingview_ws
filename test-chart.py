from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td

def callbackFunc(datas):
    print(len(datas), datas[len(datas)-1])

if __name__ == "__main__":
    pair = "ES"
    market = "futures"
    username = None
    password = None
    trading = td.TradingViewWs(pair, market, username, password)
    interval = 5
    total_candle = 240
    trading.realtime_bar_chart(interval, total_candle, callbackFunc)
