# Information
This package to fetch data from tradingview websocket
## Installation

# Create an isolated Python virtual environment
pip3 install virtualenv
virtualenv ./virtualenv --python=$(which python3)

# Activate the virtualenv
# IMPORTANT: it needs to be activated every time before you run
. virtualenv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Install
pip install -e .

# run test
python -m test

# Using:

* define a callback function get receive result

```
def callbackFunc(s):
    print(s)
```

* call websocket to get quote price or ohlcv to write a trading bot, data will be delayed 10m if don't use account premium

```
pair = "ES"

market = "futures" # 'stock' | 'futures' | 'forex' | 'cfd' | 'crypto' | 'index' | 'economic'
username = None
password = None
trading = td.TradingViewWs(pair, market, username, password)
# get quote price
trading.realtime_quote(callbackFunc)

# get ohlcv
interval = 5
total_candle = 240 # total candle to calculate indicator ex: EMA, WMA
trading.realtime_bar_chart(interval, total_candle, callbackFunc)
```

![Alt text](https://github.com/dearvn/tradingview_ws/raw/main/console.png?raw=true "result")

