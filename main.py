import os
import sys
import json
import time
import requests
import websocket
from keep_alive import keep_alive

status = "dnd"  # online/dnd/idle

GUILD_ID = 1112644273725259807
CHANNEL_ID = 1112655603102396436
SELF_MUTE = False
SELF_DEAF = False

usertokens = [
    os.getenv("TOKEN1"),
    os.getenv("TOKEN2"),
    os.getenv("TOKEN3"),
    # Add more token variables if needed
]

headers = {"Content-Type": "application/json"}

def validate_token(token):
    headers["Authorization"] = token
    validate = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
    return validate.status_code == 200

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

def run_joiner():
    os.system("clear")
    token_count = len(usertokens)
    if token_count == 0:
        print("[ERROR] Please add tokens inside Secrets.")
        sys.exit()

    valid_tokens = [token for token in usertokens if validate_token(token)]
    if len(valid_tokens) == 0:
        print("[ERROR] All tokens are invalid. Please check them again.")
        sys.exit()

    print(f"Successfully validated {len(valid_tokens)}/{token_count} tokens.")
    for i, token in enumerate(valid_tokens, start=1):
        headers["Authorization"] = token
        userinfo = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers).json()
        username = userinfo["username"]
        discriminator = userinfo["discriminator"]
        userid = userinfo["id"]
        print(f"Logged in as {username}#{discriminator} ({userid}).")
        joiner(token, status)
        print(f"Token {i}/{len(valid_tokens)} finished. Reconnecting in 30 seconds...")
        time.sleep(30)

keep_alive()
run_joiner()
