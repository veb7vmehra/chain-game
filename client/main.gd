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

func _ready():
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	$login.connect("login",self,"_on_login")
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)
	OS.set_window_size(Vector2(960,540))


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
		players[data['joined_room']].init(data['joined_room'],0,0)
		add_child(players[data['joined_room']])
	if data['action'] == 'join_error':
		pass #do something you filthy shit
	if data['action'] == 'ids':
		$Map1.show()
		$GUI.hide()
		add_child(player)
		player.set_type('knife' if data[pID][0] == '0' else 'handgun')
		player.init(pID,get_node("Map1/pos_"+data[pID]).position.x,get_node("Map1/pos_"+data[pID]).position.y)
		#player.init(pID,0,0)
		for ids in data:
			if ids != pID  and ids != 'action' and ids[3] != '_':
				print(ids+" joined for no reason")
				players[ids].set_type('knife' if data[ids][0] == '0' else 'handgun')
				players[ids].init(ids,get_node("Map1/pos_"+data[ids]).position.x,get_node("Map1/pos_"+data[ids]).position.y)
				#players[ids].init(ids,0,0)
	if data['action'] == 'entered_room':
		player = Player.instance()
		player.connect("moveplayer", self, "_moveplayer")
		player.connect("shoot", self, "_shoot")
		player.connect("knife", self, "_knife")
func _process(delta):
	_client.poll()

func _moveplayer(x,y,vx,vy,rot):
	var playerID = player.getID()
	if playerID != null:
		var data = JSON.print({"action":"move","pID":playerID,'x':x, 'y':y,'vx':vx, 'vy':vy, 'rot':rot}).to_utf8()
		_client.get_peer(1).put_packet(data)

func _on_play_pressed():
	if len($GUI/players.text) > 0:
		var data = JSON.print({"action":"play","pID":pID,"party":"1",'x':0, 'y':0, 'rot':0,'code':code}).to_utf8()
		_client.get_peer(1).put_packet(data)
	else:
		var data = JSON.print({"action":"play","pID":pID,"party":"0",'x':0, 'y':0, 'rot':0,'code':code}).to_utf8()
		_client.get_peer(1).put_packet(data)
