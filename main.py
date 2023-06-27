import os
import sys
import json
import time
import requests
import websocket
from threading import Thread
from keep_alive import keep_alive

status = "online"  # online/dnd/idle

GUILD_ID = 1112644273725259807
CHANNEL_ID = 1112655603102396436
SELF_MUTE = True
SELF_DEAF = False

usertokens = [
    os.getenv("TOKEN1"),
    os.getenv("TOKEN2"),
    os.getenv("TOKEN3"),
    # Add more tokens here as needed
]

valid_tokens = []

for token in usertokens:
    if token:
        headers = {"Authorization": token, "Content-Type": "application/json"}
        validate = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
        if validate.status_code == 200:
            valid_tokens.append(token)
        else:
            print(f"[ERROR] Token might be invalid: {token}")

if not valid_tokens:
    print("[ERROR] No valid tokens found. Please check your tokens.")
    sys.exit()

def joiner(token, status):
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
    start = json.loads(ws.recv())
    heartbeat = start['d']['heartbeat_interval']
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows 10",
                "$browser": "Google Chrome",
                "$device": "Windows"
            },
            "presence": {
                "status": status,
                "afk": False
            }
        },
        "s": None,
        "t": None
    }
    vc = {
        "op": 4,
        "d": {
            "guild_id": GUILD_ID,
            "channel_id": CHANNEL_ID,
            "self_mute": SELF_MUTE,
            "self_deaf": SELF_DEAF
        }
    }
    ws.send(json.dumps(auth))
    ws.send(json.dumps(vc))
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps({"op": 1, "d": None}))

def connect_tokens():
    threads = []
    for token in valid_tokens:
        thread = Thread(target=joiner, args=(token, status))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def run_joiner():
    os.system("clear")
    print("Logged in as:")
    for token in valid_tokens:
        headers = {"Authorization": token, "Content-Type": "application/json"}
        userinfo = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers).json()
        username = userinfo["username"]
        discriminator = userinfo["discriminator"]
        userid = userinfo["id"]
        print(f"{username}#{discriminator} ({userid})")

    while True:
        time.sleep(30)

keep_alive()
connect_tokens()
run_joiner()
