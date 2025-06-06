from ursina import *
import random
import math

app = Ursina()

window.color = color.rgb(135, 206, 235)

# Sounds
engine_sound = Audio('engine.wav', loop=True, autoplay=True)
crash_sound = Audio('crash.wav', autoplay=False)

# Ground
road = Entity(model='plane', scale=(50, 1, 500), texture='white_cube', texture_scale=(50, 500), color=color.gray, collider='box')

# Car
car = Entity(model='cube', color=color.orange, scale=(1.5, 1, 3), position=(0, 0.5, 0), collider='box')
car.velocity = Vec3(0, 0, 0)
car.rotation_y = 0

# Camera
camera.parent = car
camera.position = (0, 10, -20)
camera.rotation_x = 30

# Obstacles
obstacles = []

# Score
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)

game_over = False

def spawn_obstacle():
    x_pos = random.uniform(-10, 10)
    z_pos = car.z + random.uniform(50, 100)
    obstacle = Entity(model='cube', color=color.black, scale=(2, 2, 2), position=(x_pos, 1, z_pos), collider='box')
    obstacles.append(obstacle)

def update():
    global score, game_over

    if game_over:
        return

    # Car movement
    acceleration = 0
    turn = 0
    max_speed = 20

    if held_keys['w']:
        acceleration = 0.2
    elif held_keys['s']:
        acceleration = -0.2

    if held_keys['a']:
        turn = -60 * time.dt
    elif held_keys['d']:
        turn = 60 * time.dt

    car.rotation_y += turn * (1 if car.velocity.z > 0 else -1)
    forward = Vec3(math.sin(math.radians(car.rotation_y)), 0, math.cos(math.radians(car.rotation_y)))
    car.velocity += forward * acceleration
    car.velocity *= 0.98  # Friction
    if car.velocity.length() > max_speed:
        car.velocity = car.velocity.normalized() * max_speed

    car.position += car.velocity * time.dt

    # Camera follows behind smoothly
    camera.position = lerp(camera.position, car.world_position + Vec3(0, 10, -20), 4 * time.dt)
    camera.look_at(car.position + Vec3(0, 1, 0))

    # Obstacle movement / check
    for obs in obstacles:
        if obs.intersects(car).hit:
            crash_sound.play()
            engine_sound.stop()
            game_over_text = Text(text="GAME OVER", origin=(0, 0), scale=3, color=color.red)
            game_over = True

        if obs.z < car.z - 10:
            obstacles.remove(obs)
            destroy(obs)
            score += 1
            score_text.text = f"Score: {score}"

    # Spawn new obstacles
    if random.random() < 0.02:
        spawn_obstacle()

app.run()
