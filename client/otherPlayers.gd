extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()
var target = Vector2()
#export var weapons = ["flashlight", "handgun", "knife", "rifle", "shotgun"]
export var weapons = {"handgun":false, "knife":false}
signal keyPress(key)
#melee, knife, rifle, shotgun, handgun

var melee = load("res://assets/sfx/melee.wav")
var run = load("res://assets/sfx/run.wav")
var walk = load("res://assets/sfx/footstep.wav")
var handgun = load("res://assets/sfx/handgun.wav")
var machinegun = load("res://assets/sfx/machine-gun.wav")
var rifle = load("res://assets/sfx/rifle.wav")
var knife = load("res://assets/sfx/knife.wav")
var reload = load("res://assets/sfx/reload.wav")
var hit = load("res://assets/sfx/hit.wav")

func init(ID,x,y):
	id = ID
	position.x = 0
	position.y = 0

func getpos():
	return position

func set_type(type):
	weapons[type] = true
	$player.play(type+"_idle")

func move(x,y,vx,vy,rot):
	velocity = Vector2(vx,vy)
	target = Vector2(x,y)
	$player.rotation = rot

func hit_sfx():
	$sfx.set_stream(hit)

func _physics_process(delta):
	if position.distance_to(target) > 5:
		position = target
	elif velocity.length() > 1:
		velocity = move_and_slide(velocity)
		$player/feet.play("walk")
	else:
		$player/feet.play("idle")
