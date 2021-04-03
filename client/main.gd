extends Node

var Player = preload("res://Character.tscn")
var otherPlayers = preload("res://otherPlayers.tscn")
var player = null
# The URL we will connect to
export var websocket_url = "ws://127.0.0.1:6789"
var players = {}
var pID = null
# Our WebSocketClient instance
var _client = WebSocketClient.new()
var code = '0000'
var team
var room
var coins_hand = []
var bijli_hand = 0

func _ready():
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)
	OS.set_window_size(Vector2(960,540))

var coin = preload("res://coin.tscn")
var bijli = preload("res://bijli.tscn")

var cc = 0
var bc = 0
var coins = []
var bijlis = []
var mult = 50

func addCoin(bs,x,y):
	coins.append([coin.instance(),bs])
	coins[cc][0].position = Vector2($map/T1.position.x+int(x)*mult,$map/T1.position.y+int(y)*mult)
	$map/coins.add_child(coins[cc][0])
	cc += 1

func addBijli(x,y):
	bijlis.append(bijli.instance())
	bijlis[bc].position = Vector2($map/T1.position.x+int(x)*mult,$map/T1.position.y+int(y)*mult)
	$map/bijlis.add_child(bijlis[bc])
	bc += 1

func _closed(was_clean = false):
	print("Closed, clean: ", was_clean)
	set_process(false)

func _connected(proto = ""):
	var jdat = {'action': 'join'}
	#_client.get_peer(1).put_var(JSON.print(jdat))

func _on_data():
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	data = JSON.parse(data).result
	if data["action"] == "sent_pID":
		print("Joined with ID" + data["pID"])
		pID = data["pID"]
	if data["action"] == "new_user":
		players[data['ID']] = otherPlayers.instance()
		players[data['ID']].init(data['ID'], data['x'], data['y'])
		add_child(players[data['ID']])
		print("New User added")
	if data["action"] == "move":
		if data['pID'] == pID:
			player.move(data['x'],data['y'],data['vx'],data['vy'],data['rot'])
		else:
			players[data['pID']].move(data['x'],data['y'],data['vx'],data['vy'],data['rot'])
	if data['action'] == "joined_room":
		players[data['joined_room']] = otherPlayers.instance()
		if team==data['team']:
			players[data['joined_room']]._visiblePlayers()
		if data['role']=='in_chair':
			players[data['joined_room']].init(data['joined_room'],get_node("map/G"+data['team']).position.x,get_node("map/G"+data['team']).position.y, data['team'])
		else:
			players[data['joined_room']].init(data['joined_room'],get_node("map/F"+data['team']).position.x,get_node("map/F"+data['team']).position.y, data['team'])
		add_child(players[data['joined_room']])
	if data['action'] == "in_room":
		players[data['in_room']] = otherPlayers.instance()
		print(data)
		if team==data['team']:
			players[data['in_room']]._visiblePlayers()
		if data['role']=='in_chair':
			players[data['in_room']].init(data['in_room'],get_node("map/G"+data['team']).position.x,get_node("map/G"+data['team']).position.y, data['team'])
		else:
			players[data['in_room']].init(data['in_room'],get_node("map/F"+data['team']).position.x,get_node("map/F"+data['team']).position.y, data['team'])
		add_child(players[data['in_room']])
	if data['action'] == 'drop':
		addCoin(data['bit_size'],data['x_bit'],data['y_bit'])
		for i in range(5):
			addBijli(data['x_cur'+str(i+1)],data['y_cur'+str(i+1)])
		
	if data['action'] == 'entered_room':
		player = Player.instance()
		team=data['team']
		room=data['room']
		if data['role']=='in_chair':
			player.init(pID,get_node("map/G"+data['team']).position.x,get_node("map/G"+data['team']).position.y)
		else:
			player.init(pID,get_node("map/F"+data['team']).position.x,get_node("map/F"+data['team']).position.y)
		player.connect("moveplayer", self, "_moveplayer")
		player.connect('spot', self, "_respawnSpot")
		$map.show()
		$Sprite.hide()
		$playButton.hide()
		add_child(player)
	if data['action'] == 'respawn':
		player.init(pID,get_node("map/F"+team).position.x,get_node("map/F"+team).position.y)
		
func _process(delta):
	_client.poll()
	
func _respawnSpot(obj):
	var playerID = player.getID()
	var other = null
	for i in players: if players[i] == obj: other = i
	if playerID != null and other != null:
		if team != players[other].getTeam():
			var p1pos = player.getpos()
			var p2pos = players[other].getpos()
			var Rdata = JSON.print({"action":"spot","pID":other,'room':room}).to_utf8()
			_client.get_peer(1).put_packet(Rdata)
	else:
		for i in range(len(coins)):if coins[i][0] == obj: other = i
		if other!= null:
			if player.getpos().distance_to(coins[other][0].getpos()) < 10:
				coins_hand.append(coins[other][1])
				coins[other][0].hide()
		else:
			for i in range(len(bijlis)):if bijlis[i] == obj: other = i
			if other!= null:
				if player.getpos().distance_to(bijlis[other].getpos()) < 10:
					bijli_hand += 1
					bijlis[other].hide()
		
	
func _moveplayer(x,y,vx,vy,rot):
	var playerID = player.getID()
	if playerID != null:
		var data = JSON.print({"action":"move","pID":playerID,'x':x, 'y':y,'vx':vx, 'vy':vy, 'rot':rot, 'room': room}).to_utf8()
		_client.get_peer(1).put_packet(data)


func _on_playButton_pressed():
	var data = JSON.print({"action":"play","pID":pID,'x':0, 'y':0, 'rot':0,'code':code}).to_utf8()
	_client.get_peer(1).put_packet(data)
