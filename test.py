from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td

if __name__ == "__main__":
    pair = "btc"
    market = "crypto"
    trading = td.TradingViewWs(pair, market)

    trading.realtime()