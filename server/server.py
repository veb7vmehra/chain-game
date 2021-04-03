import asyncio
import json
import logging
import websockets
import csv
import random, string
import time
import socketserver, threading

global all_user
global parties
global rooms

threads = []
all_user = dict() #users online
parties = dict() #parties available
nr = 12 #no of participants in one room
avb = 0 #no of rooms
rooms = dict()
rooms[avb] = {"participants": 0}
available_room = "room_"+str(avb)+".txt"

async def register(ws, message):
    global avb
    global available_room
    data = json.loads(message.decode('UTF-8'))
    if rooms[avb]["participants"] < nr:
        pID = data["pID"]
        rooms[avb]["participants"] = rooms[avb]["participants"] + 1
        if rooms[avb]["participants"] <= nr/2:
            if rooms[avb]["participants"] == 1:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "team1", "role": "in_chair"}
                cong = {"action": "entered_room", "team": "team1", "role": "in_chair"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "team1", "role": "in_chair"}
                message = json.dumps(message)
            else:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "team1", "role": "field_player"}
                cong = {"action": "entered_room", "team": "team1", "role": "field_player"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "team1", "role": "in_chair"}
                message = json.dumps(message)
        else:
            if rooms[avb]["participants"] == 7:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "team2", "role": "in_chair"}
                cong = {"action": "entered_room", "team": "team2", "role": "in_chair"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "team2", "role": "in_chair"}
                message = json.dumps(message)
            else:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "team2", "role": "field_player"}
                cong = {"action": "entered_room", "team": "team2", "role": "field_player"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "team2", "role": "in_chair"}
                message = json.dumps(message)
        users = []
        if rooms[avb]["participants"] > 1:
            for key in rooms[avb].keys():
                if key != "participants" and key != pID:
                    users.append(key)
                    data = {"action": "in_room", "in_room": key, "team": rooms[avb][key]["team"], "role": rooms[avb][key]["role"]}
                    data = json.dumps(data)
                    await ws.send(data)
            await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
    else:
        avb = avb+1
        pID = data["pID"]
        rooms[avb] = dict()
        rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "team2", "role": "in_chair"}
        rooms[avb]["participants"] = 1
        cong = {"action": "entered_room", "team": "team2", "role": "in_chair"}
        cong = json.dumps(cong)
        await ws.send(cong)

async def move_state(data):
    id = data['pID']
    data = json.dumps(data)
    if len(all_user) > 1:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([all_user[user]['ws'].send(data) for user in all_user if user != id])

async def counter(websocket, path):
    pID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    all_user[pID]= {"ws":websocket,"x":"0","y":"0"}
    data = {"action": "sent_pID", "pID": pID}
    data = json.dumps(data)
    await websocket.send(data)
    #all_user[data[pID]]= {"ws":websocket,"x":"0","y":"0"}    
    try:
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "play":
                await register(websocket, message)
            elif data["action"] == "move":
                await move_state(data)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)

start_server = websockets.serve(counter, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()