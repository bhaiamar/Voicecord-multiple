import os
import sys
import json
import time
import requests
import websocket
from keep_alive import keep_alive

status = "online" #online/dnd/idle

GUILD_ID = 1029698252632752198
CHANNEL_ID = 1053585168797024286
SELF_MUTE = True
SELF_DEAF = False

# Add your tokens here as a list of strings
usertokens = [os.getenv("MTExNDgwNDg2MTMzOTQ0MzIwMQ.GxWlUg.kVXaaUdZ4IziECOCbkDgB_TdfzEl5jFTD9eDtI"), os.getenv("TOKEN2"), os.getenv("TOKEN3")]

for usertoken in usertokens:
    if not usertoken:
        print("[ERROR] Please add a token inside Secrets.")
        sys.exit()

    headers = {"Authorization": usertoken, "Content-Type": "application/json"}

    validate = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
    if validate.status_code != 200:
        print("[ERROR] Your token might be invalid. Please check it again.")
        sys.exit()

    userinfo = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers).json()
    username = userinfo["username"]
    discriminator = userinfo["discriminator"]
    userid = userinfo["id"]

def joiner(token, status):
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
    start = json.loads(ws.recv())
    heartbeat = start['d']['heartbeat_interval']
    auth = {"op": 2,"d": {"token": token,"properties": {"$os": "Windows 10","$browser": "Google Chrome","$device": "Windows"},"presence": {"status": status,"afk": False}},"s": None,"t": None}
    vc = {"op": 4,"d": {"guild_id": GUILD_ID,"channel_id": CHANNEL_ID,"self_mute": SELF_MUTE,"self_deaf": SELF_DEAF}}
    ws.send(json.dumps(auth))
    ws.send(json.dumps(vc))
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps({"op": 1,"d": None}))

def run_joiner():
  os.system("clear")
  print(f"Logged in as {username}#{discriminator} ({userid}).")
  while True:
      for usertoken in usertokens:
          joiner(usertoken, status)
      time.sleep(30)

keep_alive()
run_joiner()
