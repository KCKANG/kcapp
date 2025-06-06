from ursina import *
import random

app = Ursina()

window.color = color.rgb(135, 206, 235)  # sky blue

# Load sounds (place 'engine.wav' and 'crash.wav' in the same folder)
engine_sound = Audio('engine.wav', loop=True, autoplay=True)
crash_sound = Audio('crash.wav', autoplay=False)

# Road
road = Entity(model='cube', scale=(10, 0.1, 100), color=color.gray, collider='box')

# Car
car = Entity(model='cube', color=color.red, scale=(2, 1, 4), position=(0, 0.6, -10), collider='box')

# Obstacles
obstacles = []

# Score
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2)

game_over = False

def spawn_obstacle():
    x_pos = random.choice([-3, 0, 3])
    z_pos = car.z + 60
    obstacle = Entity(model='cube', color=color.black, scale=(2, 1, 2), position=(x_pos, 0.6, z_pos), collider='box')
    obstacles.append(obstacle)

def update():
    global score, game_over

    if game_over:
        return

    # Move car left/right
    if held_keys['a'] and car.x > -3:
        car.x -= 5 * time.dt
    if held_keys['d'] and car.x < 3:
        car.x += 5 * time.dt

    # Move obstacles toward the car
    for obs in obstacles:
        obs.z -= 10 * time.dt

        # Collision
        if obs.intersects(car).hit:
            crash_sound.play()
            engine_sound.stop()
            game_over_text = Text(text="GAME OVER", origin=(0, 0), scale=3, color=color.red)
            game_over = True

        # Increase score
        if obs.z < car.z - 5:
            score += 1
            score_text.text = f"Score: {score}"
            obstacles.remove(obs)
            destroy(obs)

    # Spawn new obstacles
    if random.random() < 0.03:
        spawn_obstacle()

app.run()
