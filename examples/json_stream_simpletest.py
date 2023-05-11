# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

import adafruit_requests
import adafruit_json_stream as json_stream
import socketpool
import ssl
import wifi
import time

pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool, ssl.create_default_context())

SCORE_URL = f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

while True:
    resp = session.get(SCORE_URL)
    json_data = json_stream.load(resp.iter_content(32))
    for event in json_data["events"]:
        if "Seattle" not in event["name"]:
            continue
        for competition in event["competitions"]:
            for competitor in competition["competitors"]:
                print(competitor["team"]["displayName"], competitor["score"])
    time.sleep(60)
