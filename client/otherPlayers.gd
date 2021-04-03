extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()
var target = Vector2()
var team

signal keyPress(key)
func init(ID,x,y, team1):
	id = ID
	position.x = x
	position.y = y
	team=team1
	$id.text=id
	
func getTeam():
	return team
	
func getID():
	return id

func getpos():
	return position

func set_type(type):
	$player.play(type+"_idle")

func move(x,y,vx,vy,rot):
	velocity = Vector2(vx,vy)
	target = Vector2(x,y)
	$player.rotation = rot

func _physics_process(delta):
	if position.distance_to(target) > 5:
		position = target
	elif velocity.length() > 1:
		velocity = move_and_slide(velocity)
		$player/feet.play("walk")
	else:
		$player/feet.play("idle")
		
func _visiblePlayers():
	$player.set_material(null)
	$id.set_material(null)
