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
SELF_MUTE = False
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
    heartbeat_interval = start['d']['heartbeat_interval'] / 1000
    session_id = None
    sequence = None

    while True:
        if ws.connected:
            data = json.loads(ws.recv())
            op = data['op']
            if op == 10:
                heartbeat_interval = data['d']['heartbeat_interval'] / 1000
                heartbeat_thread = Thread(target=send_heartbeat, args=(ws,))
                heartbeat_thread.start()
                identify_payload = {
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
                    }
                }
                ws.send(json.dumps(identify_payload))
            elif op == 11:
                print("Received heartbeat ACK")
            elif op == 9:
                print("Received invalid session, reconnecting...")
                time.sleep(5)
                joiner(token, status)
                break
            elif op == 0:
                sequence = data['s']
                if data['t'] == 'READY':
                    session_id = data['d']['session_id']
                if data['t'] == 'VOICE_SERVER_UPDATE':
                    voice_payload = {
                        "op": 4,
                        "d": {
                            "guild_id": GUILD_ID,
                            "channel_id": CHANNEL_ID,
                            "self_mute": SELF_MUTE,
                            "self_deaf": SELF_DEAF
                        }
                    }
                    ws.send(json.dumps(voice_payload))

        else:
            print("Disconnected, reconnecting...")
            time.sleep(5)
            joiner(token, status)
            break

def send_heartbeat(ws):
    while ws.connected:
        heartbeat_payload = {
            "op": 1,
            "d": None
        }
        ws.send(json.dumps(heartbeat_payload))
        time.sleep(heartbeat_interval)

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
