from __future__ import print_function

import requests,random, json, re, string
from websocket import create_connection

import json
import random
import string
import re
import pandas as pd
from datetime import datetime
from time import localtime


_API_URL_ = 'https://symbol-search.tradingview.com/symbol_search'
_WS_URL_ = "wss://data.tradingview.com/socket.io/websocket"

class TradingViewWs():
    def __init__(self, ticker, market, username = None, password = None):
        self.ticker = ticker.upper()
        self.market = market
        self._ws_url = _WS_URL_
        self._api_url = _API_URL_
        self.username = username
        self.password = password
        self.datas = []

    def get_auth_token(self):
        sign_in_url = 'https://www.tradingview.com/accounts/signin/'

        data = {"username": self.username, "password": self.password, "remember": "on"}
        headers = {
            'Referer': 'https://www.tradingview.com'
        }
        response = requests.post(url=sign_in_url, data=data, headers=headers)
        auth_token = response.json()['user']['auth_token']
        return auth_token

    def search(self, query, type):
        # type = 'stock' | 'futures' | 'forex' | 'cfd' | 'crypto' | 'index' | 'economic'
        # query = what you want to search!
        # it returns first matching item
        res = requests.get(
            f"{self._api_url}?text={query}&type={type}"
        )
        if res.status_code == 200:
            res = res.json()
            assert len(res) != 0, "Nothing Found."
            return res[0]
        else:
            print("Network Error!")
            exit(1)

    def generate_session(self, type):
        string_length = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(string_length))
        return type + random_string

    def prepend_header(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def construct_message(self, func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def create_message(self, func, paramList):
        return self.prepend_header(self.construct_message(func, paramList))

    def send_message(self, ws, func, args):
        ws.send(self.create_message(func, args))

    def send_ping_packet(self, ws, result):
        ping_str = re.findall(".......(.*)", result)
        if len(ping_str) != 0:
            ping_str = ping_str[0]
            ws.send("~m~" + str(len(ping_str)) + "~m~" + ping_str)

    def socket_quote(self, ws, callback):
        while True:
            try:
                result = ws.recv()

                if "quote_completed" in result or "session_id" in result:
                    continue

                res = re.findall("^.*?({.*)$", result)

                if len(res) != 0:
                    jsonres = json.loads(res[0])

                    if jsonres["m"] == "qsd":
                        symbol = jsonres["p"][1]["n"]
                        price = jsonres["p"][1]["v"]["lp"]
                        callback({"symbol": symbol, "price": price})
                else:
                    # ping packet
                    self.send_ping_packet(ws, result)
            except KeyboardInterrupt:
                break
            except:
                continue

    def socket_bar_chart(self, ws, callback):
        while True:
            try:
                result = ws.recv()

                if not result or "quote_completed" in result or "session_id" in result:
                    continue

                out = re.search('"s":\[(.+?)\}\]', result)
                if not out:
                    continue

                out = out.group(1)

                items = out.split(',{\"')

                if len(items) != 0:
                    for item in items:
                        item = re.split('\[|:|,|\]', item)
                        ind = int(item[1])
                        ts = datetime.fromtimestamp(float(item[4])).strftime("%Y-%m-%d, %H:%M:%S")
                        s = {"datetime": ts, "open": float(item[5]), "high": float(item[6]), "low": float(item[7]), "close": float(item[8]), "volume": float(item[9])}
                        self.datas.append(s)

                    callback(self.datas)
                else:
                    # ping packet
                    print("................retry")
                    self.send_ping_packet(ws, result)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("=========except", datetime.now(), e)
                self.send_ping_packet(ws, result)

    def get_symbol_id(self, pair, market):
        data = self.search(pair, market)

        symbol_name = data["symbol"]
        if data['type'] == 'futures':
            symbol_name = data["contracts"][0]["symbol"]

        broker = data["exchange"]
        symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
        return symbol_id

    def realtime_quote(self, callback):
        # serach btcusdt from crypto category
        symbol_id = self.get_symbol_id(self.ticker, self.market)

        # create tunnel
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        ws = create_connection(self._ws_url, headers=headers)
        session = self.generate_session("qs_")

        # Send messages
        if self.username and self.password:
            auth_token = self.get_auth_token()
            self.send_message(ws, "set_auth_token", [auth_token])
        else:
            self.send_message(ws, "set_auth_token", ["unauthorized_user_token"])

        self.send_message(ws, "quote_create_session", [session])
        self.send_message(ws, "quote_set_fields", [session, "lp"])
        self.send_message(ws, "quote_add_symbols", [session, symbol_id])

        # Start job
        self.socket_quote(ws, callback)

    def realtime_bar_chart(self, interval, total_candle, callback):
        # serach btcusdt from crypto category
        symbol_id = self.get_symbol_id(self.ticker, self.market)

        # create tunnel
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        ws = create_connection(self._ws_url, headers=headers)
        session = self.generate_session("qs_")
        chart_session = self.generate_session("cs_")

        # Then send a message through the tunnel
        if self.username and self.password:
            auth_token = self.get_auth_token()
            self.send_message(ws, "set_auth_token", [auth_token])
        else:
            self.send_message(ws, "set_auth_token", ["unauthorized_user_token"])

        self.send_message(ws, "chart_create_session", [chart_session, ""])
        self.send_message(ws, "quote_create_session", [session])
        self.send_message(ws, "switch_timezone", [chart_session, "Etc/UTC"])
        self.send_message(ws, "quote_set_fields",
                    [session, "ch", "chp", "current_session", "description", "local_description", "language",
                     "exchange",
                     "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale",
                     "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
        self.send_message(ws, "quote_add_symbols", [session, symbol_id, {"flags": ['force_permission']}])
        self.send_message(ws, "quote_fast_symbols", [session, symbol_id])

        # st='~m~140~m~{"m":"resolve_symbol","p":}'
        # p1, p2 = filter_raw_message(st)
        self.send_message(ws, "resolve_symbol", [chart_session, "symbol_1",
                                           "={\"symbol\":\""+symbol_id+"\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
        self.send_message(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", str(interval), total_candle])
        # self.send_message(ws, "create_study", [chart_session,"st4","st1","s1","ESD@tv-scripting-101!",{"text":"BNEhyMp2zcJFvntl+CdKjA==_DkJH8pNTUOoUT2BnMT6NHSuLIuKni9D9SDMm1UOm/vLtzAhPVypsvWlzDDenSfeyoFHLhX7G61HDlNHwqt/czTEwncKBDNi1b3fj26V54CkMKtrI21tXW7OQD/OSYxxd6SzPtFwiCVAoPbF2Y1lBIg/YE9nGDkr6jeDdPwF0d2bC+yN8lhBm03WYMOyrr6wFST+P/38BoSeZvMXI1Xfw84rnntV9+MDVxV8L19OE/0K/NBRvYpxgWMGCqH79/sHMrCsF6uOpIIgF8bEVQFGBKDSxbNa0nc+npqK5vPdHwvQuy5XuMnGIqsjR4sIMml2lJGi/XqzfU/L9Wj9xfuNNB2ty5PhxgzWiJU1Z1JTzsDsth2PyP29q8a91MQrmpZ9GwHnJdLjbzUv3vbOm9R4/u9K2lwhcBrqrLsj/VfVWMSBP","pineId":"TV_SPLITS","pineVersion":"8.0"}])

        # Start job
        self.socket_bar_chart(ws, callback)