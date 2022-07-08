from __future__ import print_function

import requests,pytz,random
from urllib.parse import urlparse, urlencode
from datetime import datetime, timedelta
import pandas as pd

import json
import random
import re
import string

import requests
from websocket import create_connection

_API_URL_ = 'https://symbol-search.tradingview.com/symbol_search'
_WS_URL_ = "wss://data.tradingview.com/socket.io/websocket"

class TradingViewWs():
    def __init__(self, ticker, session=None):
        self.ticker = ticker.upper()
        self._ws_url = _WS_URL_
        self._api_url = _API_URL_

    def search(query, type):
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

    def generate_session():
        string_length = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(string_length))
        return "qs_" + random_string

    def prepend_header(st):
        return "~m~" + str(len(st)) + "~m~" + st

    def construct_message(func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def create_message(func, paramList):
        return self.prepend_header(self.construct_message(func, paramList))

    def send_message(ws, func, args):
        ws.send(self.create_message(func, args))

    def send_ping_packet(ws, result):
        ping_str = re.findall(".......(.*)", result)
        if len(ping_str) != 0:
            ping_str = ping_str[0]
            ws.send("~m~" + str(len(ping_str)) + "~m~" + ping_str)

    def socket_job(ws):
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
                        #to do
                        print(f"{symbol} -> {price}")

                else:
                    # ping packet
                    self.send_ping_packet(ws, result)
            except:
                continue

    def get_symbol_id(pair, market):
        data = self.search(pair, market)

        symbol_name = data["symbol"]
        broker = data["exchange"]
        symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
        print(symbol_id, end="\n\n")
        return symbol_id

    def realtime(pair, market):

        # serach btcusdt from crypto category
        symbol_id = self.get_symbol_id(pair, market)

        # create tunnel
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        ws = create_connection(self._ws_url, headers=headers)
        session = self.generate_session()

        # Send messages
        self.send_message(ws, "quote_create_session", [session])
        self.send_message(ws, "quote_set_fields", [session, "lp"])
        self.send_message(ws, "quote_add_symbols", [session, symbol_id])

        # Start job
        self.socket_job(ws)