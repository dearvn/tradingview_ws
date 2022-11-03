from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td

def callbackFunc(datas):
    print(len(datas), datas[len(datas)-1])

if __name__ == "__main__":
    pair = "ES"
    market = "futures"
    trading = td.TradingViewWs(pair, market)

    trading.realtime_chart(callbackFunc)
