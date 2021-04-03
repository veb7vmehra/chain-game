import asyncio
import json
import websockets
import random, string
import time
import threading
import math

global all_user
global parties
global rooms

threads = []
all_user = dict() #users online
parties = dict() #parties available
nr = 4#no of participants in one room
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
        message = "a"
        if rooms[avb]["participants"] <= nr/2:
            if rooms[avb]["participants"] == 1:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "1", "role": "in_chair", "blocks": [], "bits": [], "cur": 0, "backup": 0, "fake": 0}
                cong = {"action": "entered_room", "team": "1", "role": "in_chair", "room": avb}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "1", "role": "in_chair"}
                message = json.dumps(message)
            else:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "1", "role": "field_player", "bits": 0, "cur": 0, "bit_size": 0, "hack": -1}
                cong = {"action": "entered_room", "team": "1", "role": "field_player", "room": avb}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "1", "role": "field_player"}
                message = json.dumps(message)
        else:
            if rooms[avb]["participants"] == 3:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "2", "role": "in_chair", "blocks": [], "bits": [], "cur": 0, "backup": 0, "fake": 0}
                cong = {"action": "entered_room", "team": "2", "role": "in_chair", "room": avb}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "2", "role": "in_chair"}
                message = json.dumps(message)
            else:
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "2", "role": "field_player", "bits": 0, "cur": 0, "bit_size": 0, "hack": -1}
                cong = {"action": "entered_room", "team": "2", "role": "field_player", "room": avb}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID, "team": "2", "role": "field_player"}
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
        rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0", "team": "1", "role": "in_chair", "blocks": [], "bits": [], "cur": 0, "backup": 0, "fake": 0}
        rooms[avb]["participants"] = 1
        cong = {"action": "entered_room", "team": "1", "role": "in_chair", "room": avb}
        cong = json.dumps(cong)
        await ws.send(cong)

async def move_state(data):
    pid = data['pID']
    data = json.dumps(data)
    users = []
    for key in rooms[data["room"]].keys():
        if key != "participants" and key != data["pID"]:
            users.append(key)
    await asyncio.wait([all_user[user]['ws'].send(data) for user in all_user if user in users])

async def respawn(data):
    d = {"action": "respawn"}
    d = json.dumps(d)
    users = []
    for key in rooms[data["room"]].keys():
        if key != "participants" and key != data["pID"]:
            users.append(key)
    await asyncio.wait([all_user[user]['ws'].send(d) for user in all_user if user in users])

async def eject(data):
    pid = data["pID"]
    for key in rooms[data["room"]].keys():
        if key != "participants":
            if rooms[data["room"]][key]["team"] == data["team"] and rooms[data["room"]][key]["role"] == "in_chair":
                if "fake" in data.keys():
                    if data["fake"] == data["team"]:
                        rooms[data["room"]][key]["fake"] = 1
                rooms[data["room"]][key]["bits"].append(rooms[data["room"]][pid]["bit_size"])
                rooms[data["room"]][key]["cur"] += rooms[data["room"]][pid]["cur"]
                message = {"action": "eject", "bit_size": rooms[data["room"]][pid]["bit_size"], "cur": rooms[data["room"]][pid]["cur"]}
                message = json.dumps(message)
                await all_user[key]["ws"].send(message)
                break
    rooms[data["room"]][pid]["bits"] = 0
    rooms[data["room"]][pid]["bit_size"] = 0
    rooms[data["room"]][pid]["cur"] = 0
    message = {"action": "eject", "bit_size": 0, "cur": 0, "bits": 0}
    message = json.dumps(message)
    await all_user[pid]["ws"].send(message)

async def create(data):
    pid = data["pID"]
    for key in rooms[data["room"]].keys():
        if key != "participants":
            if rooms[data["room"]][key]["team"] == data["team"] and rooms[data["room"]][key]["role"] == "in_chair" and rooms[data["room"]][key]["cur"] > 0:
                if rooms[data["room"]][key]["fake"] == 1:
                    rooms[data["room"]][key]["blocks"] = []
                    message = {"action": "shit", "blocks": []}
                    message = json.dumps(message)
                    await all_user[key]['ws'].send(message)
                    break
                rooms[data["room"]][key]["blocks"].append(rooms[data["room"]][key]["bits"][0])
                rooms[data["room"]][key]["bits"].pop(0)
                rooms[data["room"]][key]["cur"] -= 1
                message = {"action": "create", "bits": rooms[data["room"]][key]["bits"], "cur": rooms[data["room"]][key]["cur"], "blocks": rooms[data["room"]][key]["blocks"]}
                message = json.dumps(message)
                await all_user[key]["ws"].send(message)
                break
    message = {"action": "create"}
    message = json.dumps(message)
    await all_user[pid]['ws'].send(message)

async def hack(data):
    pid = data["pID"]
    n = 0
    for key in rooms[data["room"]].keys():
        if key != "participants":
            if rooms[data["room"]][key]["team"] == data["team"] and rooms[data["room"]][key]["role"] == "in_chair":
                n = len(rooms[data["room"]][key]["blocks"])
                break
    rooms[data["room"]][pid]["hack"] = n
    message = {"action": "hack", "hack": n}
    message = json.dumps(message)
    await all_user[pid]["ws"].send(message)
    
async def hacked(data):
    pid = data["pID"]
    for key in rooms[data["room"]].keys():
        if key != "participants":
            if rooms[data["room"]][key]["team"] == data["team"] and rooms[data["room"]][key]["role"] == "in_chair":
                rooms[data["room"]][key]["blocks"] = rooms[data["room"]][key]["team"][:data[hack]]
                message = {"action": "hacked", "hack": rooms[data["room"]][key]["blocks"]}
                message = json.dumps(message)
                await all_user[key]["ws"].send(message)
                break
    message = {"action": "hacked", "hack": -1}
    message = json.dumps(message)
    await all_user[pid]["ws"].send(message)

async def sell(data):
    pid = data["pID"]
    rooms[data["room"]][pid]["cur"] = 100*data["bit_size"]
    rooms[data["room"]][pid]["bits"].pop(data["bit_size"])
    message = {"action": sell, "cur": rooms[data["room"]][pid]["cur"], "bits": rooms[data["room"]][pid]["bits"]}
    message = json.dumps(message)
    await all_user[pid]["ws"].send(message)

async def bot(data):
    pid = data["pID"]
    if rooms[data["room"]][pid]["cur"] >= 50:
        rooms[data["room"]][pid]["cur"] -= 50
        message = {"action": "bot_charge", "cur": rooms[data["room"]][pid]["cur"]}
        message = json.dumps(message)
        await all_user[pid]['ws'].send(message)
        if data["team"] == "team1":
            x = 0
            y = 0
            users = []
            message = {"action": "bot", "x": x, "y": y}
            message = json.dumps(message)
            for user in rooms[data["room"]].keys():
                if user != "participants":
                    users.append(user)
            await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        else:
            x = 10
            y = 10
            users = []
            message = {"action": "bot", "x": x, "y": y}
            message = json.dumps(message)
            for user in rooms[data["room"]].keys():
                if user != "participants":
                    users.append(user)
            await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])

async def backup(data):
    pid = data["pID"]
    cost = data["no"]*100
    if rooms[data["room"]][pid]["cur"] >= cost:
        rooms[data["room"]][pid]["cur"] -= cost
        rooms[data["room"]][pid]["backup"] += data["no"]
        message = {"action": "backup", "backup": rooms[data["room"]][pid]["backup"], "cur": rooms[data["room"]][pid]["cur"]}
        message = json.dumps(message)
        await all_user[pid]["ws"].send(message)

async def recall(data):
    pid = data["pID"]
    if rooms[data["room"]][pid]["backup"] != 0:
        rooms[data["room"]][pid]["blocks"] = [rooms[data["room"]][pid]["backup"]]
    message = {"action": "recall", "blocks": rooms[data["room"]][pid]["blocks"]}
    message = json.dumps(message)
    await all_user[pid]['ws'].send(message)

async def change(data):
    id_1 = data["pID"]
    id_2 = data["tID"]
    temp = rooms[data["room"]][id_1]
    rooms[data["room"]][id_1] = rooms[data["room"]][id_2]
    rooms[data["room"]][id_2] = temp
    users = []
    message = {"action": "change", "in_chair": id_2, "field_guy": id_1}
    message = json.dumps(message)
    for user in rooms[data["room"]].keys():
        if user != "participants":
            users.append(user)
    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])

async def fake(data):
    vals = [5, 7, 9, 11, 13, 15]
    pillars = [1, 2]
    x = [0, 10]
    y = [0, 10]
    bit = random.choice(vals)
    pillar = random.choice(pillars)
    alpha_bit = 2*math.pi*random.random()
    r_bit = bit * math.sqrt(random.random())
    x_bit = bit * math.cos(alpha_bit) + x[pillar]
    y_bit = bit * math.sin(alpha_bit) + y[pillar]
    message = {"action": "drop", "x_bit": x_bit, "y_bit": y_bit, "bit_size": bit, "fake": data["team"]}
    message = json.dump(message)
    for user in rooms[data["room"]].keys():
        if user != "participants":
            await all_user[user]['ws'].send(message)

async def collect(data):
    pid = data['pID']
    if data["type"] == "bits":
        if rooms[data["room"]][pid]["bits"] < 1:
            rooms[data["room"]][pid]["bits"] += 1
            rooms[data["room"]][pid]["bit_size"] = data["size"]
            message = "a"
            if "fake" in data.keys():
                message = {"bits": 1, "bit_size": data["size"], "fake": data["fake"]}
                message = json.dumps(message)
            else:
                message = {"bits": 1, "bit_size": data["size"]}
                message = json.dumps(message)
            await all_user[pid]["ws"].send(message)
            data = json.dumps(data)
            if len(all_user) > 1:  # asyncio.wait doesn't accept an empty list
                await asyncio.wait([all_user[user]['ws'].send(data) for user in all_user if user != pid])
    if data["type"] == "cur":
        if rooms[data["room"]][pid]["cur"] < 5:
            rooms[data["room"]][pid]["cur"] += 1
            message = {"cur": rooms[data["room"]][pid]["cur"]}
            message = json.dumps(message)
            await all_user[pid]["ws"].send(message)
            data = json.dumps(data)
            if len(all_user) > 1:  # asyncio.wait doesn't accept an empty list
                await asyncio.wait([all_user[user]['ws'].send(data) for user in all_user if user != pid])

async def pingpong():
    while True:
        for user in all_user:
            if not user['ws'].connected:
                for room in rooms:
                    if user in room.keys():
                        for u in room.keys():
                            if u != "participant" and u != user:
                                message = {"action": "removed", "user": user}
                                message = json.dumps(message)
                                await all_user[u]['ws'].send(message)
                        break
                all_user.pop(user)

async def unregister(websocket):
    [all_user.remove(user) for user in all_user if user[1] == websocket]

async def coins():
    global rooms
    vals = [5, 7, 9, 11, 13, 15]
    pillars = [1, 2]
    x = [0, 10]
    y = [0, 10]
    for room in rooms:
        bit = random.choice(vals)
        pillar = random.choice(pillars)
        alpha_bit = 2*math.pi*random.random()
        r_bit = bit * math.sqrt(random.random())
        x_bit = bit * math.cos(alpha_bit) + x[pillar]
        y_bit = bit * math.sin(alpha_bit) + y[pillar]
        x_cur = []
        y_cur = []
        for i in range(5):
            alpha_bit = 2*math.pi*random.random()
            r_bit = bit * math.sqrt(random.random())
            x_cur.append(bit * math.cos(alpha_bit) + x[pillar])
            y_cur.append(bit * math.sin(alpha_bit) + y[pillar])
        message = {"action": "drop", "bit_size": bit, "x_bit": x_bit, "y_bit": y_bit, "x_cur1": x_cur[0], "y_cur1": y_cur[0], "x_cur2": x_cur[1], "y_cur2": y_cur[1], "x_cur3": x_cur[2], "y_cur3": y_cur[2], "x_cur4": x_cur[3], "y_cur4": y_cur[3], "x_cur5": x_cur[4], "y_cur5": y_cur[4]}
        message = json.dump(message)
        for key in room.keys():
            if key != "participants":
                await room[key]['ws'].send(message)
    time.sleep(10)
    coins()

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
            elif data["action"] == "collect" and rooms[data["room"]][pID]["role"] == "field_player":
                await collect(data)
            elif data["action"] == "eject" and rooms[data["room"]][pID]["role"] == "field_player":
                await eject(data)
            elif data["action"] == "create" and rooms[data["room"]][pID]["role"] == "field_player":
                await create(data)
            elif data["action"] == "hack" and rooms[data["room"]][pID]["role"] == "field_player":
                await hack(data)
            elif data["action"] == "hacked" and rooms[data["room"]][pID]["role"] == "field_player":
                await hacked(data)
            elif data["action"] == "sell" and rooms[data["room"]][pID]["role"] == "in_chair":
                await sell(data)
            elif data["action"] == "bot" and rooms[data["room"]][pID]["role"] == "in_chair":
                await bot(data)
            elif data["action"] == "backup" and rooms[data["room"]][pID]["role"] == "in_chair":
                await backup(data)
            elif data["action"] == "recall" and rooms[data["room"]][pID]["role"] == "in_chair":
                await recall(data)
            elif data["action"] == "change" and rooms[data["room"]][pID]["role"] == "in_chair":
                await change(data)
            elif data["action"] == "fake" and rooms[data["room"]][pID]["role"] == "in_chair":
                await fake(data)
            elif data["action"] == "spot":
                await respawn(data)
    finally:
        await unregister(websocket)

start_server = websockets.serve(counter, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
t = threading.Thread(target=coins)
threads.append(t)
t.start()
k = threading.Thread(target=pingpong)
threads.append(k)
k.start()
asyncio.get_event_loop().run_forever()