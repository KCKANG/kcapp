from ursina import *

app = Ursina()

player = Entity(model='cube', color=color.orange, scale=(1,2,1), position=(0,1,0))
ground = Entity(model='plane', scale=10, color=color.green, collider='box')

camera.position = (0, 10, -20)
camera.rotation_x = 30

def update():
    if held_keys['a']:
        player.x -= 4 * time.dt
    if held_keys['d']:
        player.x += 4 * time.dt
    if held_keys['space']:
        player.y += 4 * time.dt  # very simple jump

app.run()
