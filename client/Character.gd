extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()
var state = false
signal moveplayer(x,y,vx,vy,rot)
var target = Vector2()

signal spot(ray)

func init(ID,x,y):
	id = ID
	position.x = x
	position.y = y
	$id.text=id

#emit_signal("knife",$RayCast2D.get_collider())

func getID():
	return id

func getpos():
	return position

func getx():
	return position.x

func gety():
	return position.y

func _input(event):
	if event.is_action_pressed('scroll_up'):
		$Camera2D.zoom = $Camera2D.zoom - Vector2(0.1, 0.1)
	if event.is_action_pressed('scroll_down'):
		$Camera2D.zoom = $Camera2D.zoom + Vector2(0.1, 0.1)
	
func move(x, y, vx, vy, rot):
	velocity = Vector2(vx,vy)
	$player.rotation = rot
	
func get_input():
	$player.look_at(get_global_mouse_position())
	velocity = Vector2()
	if Input.is_action_pressed('run'):
		speed = 250
	else:
		speed = 150
	if Input.is_action_pressed('ui_right'):
		velocity = Vector2(0, speed).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("right")
	if Input.is_action_pressed('ui_left'):
		velocity = Vector2(0, -speed).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("left")
	if Input.is_action_pressed('ui_down'):
		velocity = Vector2(-speed, 0).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("walk")
	if Input.is_action_pressed('ui_up'):
		velocity = Vector2(speed, 0).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("walk")

	if velocity == Vector2():
		$player/feet.play("idle")
	$CollisionShape2D.rotation_degrees = $player.rotation_degrees - 90
	$RayCast2D.rotation_degrees = $player.rotation_degrees
	velocity = velocity.normalized() * speed
	emit_signal("moveplayer",position.x,position.y,velocity.x,velocity.y,$player.rotation)
	emit_signal("spot",_getCollindingStatus())

func _physics_process(delta):
	get_input()
	move_and_slide(velocity)
	
func _getCollindingStatus():
	return $RayCast2D.get_collider()
	
