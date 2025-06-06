from ursina import *

app = Ursina()

# Load sounds
engine_sound = Audio('engine.wav', loop=True, autoplay=False)
honk_sound = Audio('honk.wav', autoplay=False)

# Ground
ground = Entity(model='plane', scale=50, texture='white_cube', texture_scale=(50,50), collider='box', color=color.gray)

# Car (simple cube as placeholder)
car = Entity(model='cube', color=color.red, scale=(1.5, 0.5, 3), position=(0, 0.25, 0), collider='box')

camera.parent = car
camera.position = (0, 3, -10)
camera.rotation_x = 15

speed = 5
turn_speed = 100

def update():
    move = held_keys['w'] - held_keys['s']
    turn = held_keys['a'] - held_keys['d']

    car.rotation_y += turn * turn_speed * time.dt
    car.position += car.forward * move * speed * time.dt

    # Sound logic
    if move != 0 and not engine_sound.playing:
        engine_sound.play()
    elif move == 0 and engine_sound.playing:
        engine_sound.stop()

def input(key):
    if key == 'space':
        honk_sound.play()

app.run()