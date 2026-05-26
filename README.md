# Assteroids 🚀

A small **Asteroids-style** arcade game written in Python with [Pygame](https://www.pygame.org/). You pilot a triangular ship, rotate, thrust, and shoot asteroids that drift in from the edges of the screen. When you hit a large asteroid it splits into two smaller ones — when you hit the smallest one it disappears. If an asteroid touches your ship, the game ends.

This project is intentionally small and was built as a learning exercise. The README below is written for people who are **new to Python, OOP, or game programming** — every file is explained, and every "weird" pattern (sprite groups, delta time, vector rotation, circle-circle collision) has a section of its own.

---

## Table of Contents

1. [What you'll learn from this project](#what-youll-learn-from-this-project)
2. [Gameplay & Controls](#gameplay--controls)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Installation & Running](#installation--running)
6. [High-Level Architecture](#high-level-architecture)
7. [The Game Loop, Step by Step](#the-game-loop-step-by-step)
8. [Module-by-Module Walkthrough](#module-by-module-walkthrough)
9. [Core Concepts Explained](#core-concepts-explained)
10. [Configuration & Tuning](#configuration--tuning)
11. [The Logging Helper](#the-logging-helper)
12. [Known Issues & Ideas for Improvement](#known-issues--ideas-for-improvement)
13. [Credits](#credits)

---

## What you'll learn from this project

If you read the source alongside this README, you'll come away understanding:

- The classic **game loop** pattern (input → update → collide → draw → repeat).
- **Delta time** and why frame-rate-independent movement matters.
- **Object-oriented programming** with inheritance (`CircleShape` → `Player`, `Asteroid`, `Shot`).
- **Pygame sprite groups** and how they decouple "what exists" from "what gets updated/drawn".
- **2D vector math**: rotation, normalization, scaling, and distance.
- A simple, fast form of **collision detection** (circle vs. circle).
- A minimal, dependency-free **state/event logger** that uses Python introspection to dump JSON lines.

---

## Gameplay & Controls

| Action            | Key / Button             |
| ----------------- | ------------------------ |
| Rotate left       | `A`                      |
| Rotate right      | `D`                      |
| Thrust forward    | `W`                      |
| Thrust backward   | `S`                      |
| Boost (2× speed)  | Hold `Left Shift`        |
| Shoot             | `Space`, Left or Right Mouse |
| Quit              | Close the window         |

**Rules of the game:**

- Asteroids constantly spawn from the four edges of the screen and drift across.
- Asteroids come in 3 sizes. Hitting a large one splits it into two smaller ones; hitting the smallest size destroys it outright.
- Touching any asteroid with your ship prints `Game over!` to the terminal and exits.

---

## Tech Stack

- **Python ≥ 3.13** (see `.python-version`)
- **Pygame 2.6.1** (the only runtime dependency, declared in `pyproject.toml`)
- Optionally: **[uv](https://docs.astral.sh/uv/)** as a fast package manager (a `uv.lock` is included)

---

## Project Structure

```
assteroids/
├── main.py            # Entry point + game loop
├── constants.py       # Tunable game constants (sizes, speeds, cooldowns)
├── circleshape.py     # Base class for every collidable round thing
├── player.py          # The triangular ship the user controls
├── asteroid.py        # A drifting circle that splits when hit
├── asteroidfield.py   # Spawner: emits asteroids from random edges
├── shot.py            # A small bullet fired by the player
├── logger.py          # Optional per-frame JSONL state/event logger
├── pyproject.toml     # Project metadata & dependencies
├── uv.lock            # Lockfile (uv)
└── .python-version    # Pinned Python version
```

---

## Installation & Running

### Option A — Using `uv` (recommended, fastest)

```bash
git clone <this-repo-url>
cd assteroids
uv sync
uv run python main.py
```

### Option B — Using plain `pip` + `venv`

```bash
git clone <this-repo-url>
cd assteroids
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install "pygame==2.6.1"
python main.py
```

If a Pygame window opens with an orange background, a black triangle in the middle, and circles drifting in from the edges — you're good.

---

## High-Level Architecture

The game is built on three big ideas:

1. **A single game loop** in `main.py` that runs ~60 times per second.
2. **A class hierarchy** rooted at `CircleShape`, so every collidable object shares the same fundamental shape (a circle with a position, velocity, and radius).
3. **Pygame sprite groups** that act like "buckets" for objects, so the game loop can update or draw many objects at once without knowing what type they are.

Visually:

```
                      ┌─────────────────────┐
                      │      main.py        │
                      │   (the game loop)   │
                      └──────────┬──────────┘
                                 │ creates & ticks
        ┌────────────────────────┼─────────────────────────┐
        ▼                        ▼                         ▼
  ┌───────────┐           ┌────────────┐           ┌──────────────┐
  │ updatable │           │  drawable  │           │  asteroids   │
  │  (Group)  │           │   (Group)  │           │   (Group)    │
  └─────┬─────┘           └──────┬─────┘           └──────┬───────┘
        │ .update(dt)            │ .draw(screen)         │ collision checks
        ▼                        ▼                        ▼
   Player, Asteroid,        Player, Asteroid,         Asteroid only
   Shot, AsteroidField      Shot
```

Every object registers itself into one or more of these groups automatically via a class-level `containers` attribute — this is the trick that keeps `main.py` so short.

---

## The Game Loop, Step by Step

Open `main.py` and follow along. The core loop looks like this:

```46:63:main.py
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #listen for quit in pygame window
                return
        updatable.update(dt) # update the player rotation status
        for asteroid in asteroids:
            if asteroid.collides(player):
                print("Game over!")
                sys.exit()
            for shot in shots:
                if asteroid.collides(shot):
                    asteroid.split()
                    shot.kill()
        dt = clock.tick(60) / 1000 #limit the FPS to 60
        screen.fill("orange") # fill the screen
        for object in drawable:
            object.draw(screen) # draw the objects on the screen
        pygame.display.flip() #recycle the screen
```

What happens each iteration ("frame"):

1. **Handle window events.** If the user clicks the close button, the function returns and the program exits.
2. **Update all objects.** Calling `updatable.update(dt)` calls `.update(dt)` on every sprite in the group — that's the player, every asteroid, every bullet, and the spawner.
3. **Check collisions.**
   - If any asteroid touches the player → game over.
   - If any asteroid touches a bullet → the asteroid splits and the bullet disappears.
4. **Tick the clock.** `clock.tick(60)` caps the frame rate at 60 FPS *and* returns how many milliseconds passed since the last call. We convert that to seconds (`/ 1000`) and store it as `dt` — the "delta time" used by every `update()` method.
5. **Clear the screen.** `screen.fill("orange")` paints over the previous frame.
6. **Redraw everything.** Each object in `drawable` paints itself.
7. **Flip the back buffer to the front.** `pygame.display.flip()` makes the new frame visible. This double-buffering prevents flicker.

That's the whole game in 18 lines.

---

## Module-by-Module Walkthrough

### `constants.py` — the game's "settings"

```1:16:constants.py
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 0.8  # seconds
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
BOOST_SPEED = 400

PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 0.3
SHOT_RADIUS = 5
```

Every "magic number" lives here. Want a bigger ship, faster bullets, or more frequent asteroids? This is the only file you need to touch.

> **Beginner note:** `from constants import *` (used by other modules) means "import every public name from this file". That's why `Player`, `Asteroid`, etc. can use `PLAYER_SPEED`, `ASTEROID_MIN_RADIUS`, and so on directly.

### `circleshape.py` — the base class

```5:26:circleshape.py
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt):
        # sub-classes must override
        pass

    # If distance is less than or equal to r1 + r2, the circles are colliding. If not, they aren't.
    def collides(self, other):
        return self.position.distance_to(other.position) <= self.radius + other.radius # return True/False
```

This class does three important jobs:

1. **It inherits from `pygame.sprite.Sprite`**, so anything that extends `CircleShape` *is* a sprite and can live in sprite groups.
2. **It auto-registers** the object into any sprite groups the subclass declares via `containers`. That's the "magic" that allows `Player(...)` (in `main.py`) to automatically appear inside `updatable` and `drawable` without any extra code.
3. **It defines `collides()` once** for every subclass — see the [Collision detection](#3-collision-detection-circle-vs-circle) section below.

### `player.py` — the ship

The player is a `CircleShape` that draws itself as a triangle and reads keyboard/mouse input every frame.

```30:48:player.py
    def update(self, dt):
        self.timer -= dt
        keys = pygame.key.get_pressed() # listen for keys "getting pressed"
        mouse = pygame.mouse.get_pressed() # listen for mouse buttons "getting pressed"
        speed = BOOST_SPEED if keys[pygame.K_LSHIFT] else PLAYER_SPEED
        if keys[pygame.K_a]:
            self.rotate(-dt) # rotate left
        if keys[pygame.K_d]:
            self.rotate(dt) # rotate right
        if keys[pygame.K_w]:
            self.move(dt, speed)
        if keys[pygame.K_s]:
            self.move(-dt, speed)
        if keys[pygame.K_SPACE]: # shoot if space bar pressed
            self.shoot()
        if mouse[0]: # shoot if left mouse button is pressed
            self.shoot()
        if mouse[2]: # shoot if right mouse button is pressed
            self.shoot()
```

Two patterns worth pointing out:

- `self.timer -= dt` and the `if self.timer > 0: return` check inside `shoot()` form a **cooldown**. You can't fire faster than once every `PLAYER_SHOOT_COOLDOWN` seconds (0.3 s) no matter how hard you mash the button.
- `self.triangle()` returns three points around the player's position, rotated by `self.rotation` — that's how the ship visibly turns when you press A/D.

### `asteroid.py` — the obstacles

```7:28:asteroid.py
class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "black", self.position, self.radius, 2)

    def update(self, dt):
        self.position += (self.velocity * dt)

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        random_angle = random.uniform(20, 50)
        vector_a = self.velocity.rotate(random_angle)
        vector_b = self.velocity.rotate(-random_angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid.velocity = vector_a * 1.2
        asteroid = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid.velocity = vector_b * 1.2
```

- `update(dt)` does the simplest physics step there is: `position += velocity * dt`. That's frame-rate independent movement in one line.
- `split()` is where the "Asteroids" gameplay magic lives. When hit, the asteroid:
  1. Removes itself from all groups via `self.kill()` (a method inherited from `pygame.sprite.Sprite`).
  2. If it was already the smallest size, stops there.
  3. Otherwise it spawns **two** new smaller asteroids whose velocities are the parent's velocity rotated by ±20–50°, then sped up by 20% — so children visibly fan out and move faster than the parent.

### `asteroidfield.py` — the spawner

```31:51:asteroidfield.py
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_SPAWN_RATE:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
```

`AsteroidField` is itself a sprite — but an invisible one. It has no `draw()` method, only an `update()`. Every `ASTEROID_SPAWN_RATE` seconds (0.8 s), it:

1. Picks one of four edges at random (left, right, top, bottom).
2. Picks a random speed between 40 and 100 pixels/second.
3. Picks a random starting position somewhere along that edge.
4. Rotates the velocity by a random ±30° angle so asteroids don't all fly perfectly straight.
5. Picks a random size (1×, 2×, or 3× `ASTEROID_MIN_RADIUS`).

The `edges` class variable is a clever little table — each entry pairs a **direction vector** with a **function** that, given a random number 0–1, returns a position somewhere along that edge.

### `shot.py` — the bullets

```5:13:shot.py
class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(screen, "black", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt
```

The simplest class in the project — a small black circle that moves in a straight line in whichever direction the ship was pointing when it was fired. Notice it's structurally identical to `Asteroid` minus the `split()` behavior.

### `main.py` — wiring everything together

```26:40:main.py
    clock = pygame.time.Clock() # declare clock as instance of pygame.time.Clock()
    updatable = pygame.sprite.Group() # declare updatable objects group
    drawable = pygame.sprite.Group() # declare drawable objects group
    asteroids = pygame.sprite.Group() # declare asteroid objects group
    shots = pygame.sprite.Group() # declare shots objects group

    Player.containers = (updatable, drawable) # add class variable "containers" to Player to store groups
    Asteroid.containers = (asteroids, updatable, drawable) # add class variable "containers" to Asteroid to store groups
    AsteroidField.containers = (updatable) # add class variable "containers" to AsteroidField to store groups
    Shot.containers = (shots, updatable, drawable) # add class variable "containers" to Shots to store groups

    asteroid_field = AsteroidField() # declare variable to store the Asteroid Field as instance of AsteroidField()

    # declare Player as instance of Player(CircleShape)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
```

Note how `containers` is set on the **class itself**, not on individual instances. This means *every* future `Asteroid(...)` will automatically be added to `asteroids`, `updatable`, and `drawable` — no bookkeeping required.

---

## Core Concepts Explained

### 1. The game loop & frame timing

A game loop is just a `while True:` that drives everything. The catch is that computers run at different speeds — a loop that moves the player "5 pixels per frame" will be fast on a 240 Hz monitor and slow on a 30 Hz one.

The fix is **delta time** (`dt`):

```python
dt = clock.tick(60) / 1000   # seconds since the last frame
self.position += self.velocity * dt
```

By multiplying speed by `dt`, an object set to move at `200 pixels/second` always moves 200 pixels per second of *real time*, regardless of frame rate. `clock.tick(60)` also caps the loop at 60 FPS so it doesn't burn CPU.

### 2. Sprites and sprite groups

`pygame.sprite.Sprite` is a base class for "anything that lives on screen". `pygame.sprite.Group` is essentially a smart list of sprites. When you call `group.update(dt)`, Pygame calls `.update(dt)` on every sprite in the group.

This project uses **four groups** to organize the same objects in different ways:

| Group       | Contains                            | Used for       |
| ----------- | ----------------------------------- | -------------- |
| `updatable` | Player, Asteroid, Shot, AsteroidField | Calling `.update(dt)` each frame |
| `drawable`  | Player, Asteroid, Shot              | Calling `.draw(screen)` each frame |
| `asteroids` | Asteroid only                       | Collision checks |
| `shots`     | Shot only                           | Collision checks |

One object can live in many groups simultaneously, and calling `.kill()` on it removes it from *all* of them at once — that's how dead asteroids and spent bullets vanish.

### 3. Collision detection (circle vs. circle)

Two circles overlap if the distance between their centers is less than or equal to the sum of their radii:

```python
def collides(self, other):
    return self.position.distance_to(other.position) <= self.radius + other.radius
```

That's it. No bounding boxes, no pixel-perfect checks. Because every collidable thing in this game inherits from `CircleShape`, the same one-liner works for player↔asteroid and asteroid↔shot.

### 4. 2D vectors with `pygame.Vector2`

A `Vector2` is just an `(x, y)` pair with helpful methods:

- `vec_a + vec_b` — add two vectors (used to move objects: `position += velocity * dt`).
- `vec * scalar` — scale a vector (used to apply speed to a direction).
- `vec.rotate(angle_in_degrees)` — rotate around the origin (used for ship turning, bullet direction, and asteroid splitting).
- `vec.distance_to(other)` — Euclidean distance (used in collision).

For example, the ship calculates its "forward direction" by starting with the unit vector `(0, 1)` ("down" in screen coordinates) and rotating it by the ship's current angle:

```python
forward = pygame.Vector2(0, 1).rotate(self.rotation)
self.position += forward * speed * dt
```

### 5. Inheritance in plain English

`Player`, `Asteroid`, and `Shot` all **inherit from** `CircleShape`. That means each of them automatically gets `position`, `velocity`, `radius`, and `collides()` for free, and only has to override `draw()` and `update()` to define its own behavior.

This is why adding a new kind of object (say, a power-up) would only take ~15 lines of code — most of the infrastructure already exists in the base class.

---

## Configuration & Tuning

All the dials are in `constants.py`. A few fun experiments for beginners:

| Try changing…           | …and you'll see                                   |
| ----------------------- | ------------------------------------------------- |
| `ASTEROID_SPAWN_RATE`   | Lower it (e.g. `0.2`) for chaos, raise it for calm. |
| `PLAYER_SHOOT_COOLDOWN` | Set to `0.05` for a machine-gun ship.             |
| `PLAYER_SPEED`          | Raise it to `500` — much harder to control!       |
| `ASTEROID_KINDS`        | Set to `5` for *huge* starting asteroids that split many times. |
| `SHOT_RADIUS`           | Bump to `15` for "shotgun" feel.                  |

You don't need to touch any other file to make these tweaks.

---

## The Logging Helper

`logger.py` is a small, **optional** helper that nothing in `main.py` currently imports. It exists so you (or a teacher) can drop a one-liner into the game loop and get a JSONL file out the other side describing what happened.

It exports two functions:

- `log_state()` — call it once per frame. It uses `inspect` to peek at the caller's local variables, detects any `pygame.sprite.Group`s, and dumps a snapshot of every sprite's `position`, `velocity`, `radius`, and `rotation`. It samples one snapshot per second for up to 16 seconds and writes to `game_state.jsonl`.
- `log_event(event_type, **details)` — call it whenever something interesting happens (a shot fired, an asteroid split, etc.). It appends one JSON line per call to `game_events.jsonl`.

Example wiring inside `main()`:

```python
from logger import log_state, log_event

# inside the loop, just before pygame.display.flip():
log_state()

# inside the collision branch:
if asteroid.collides(shot):
    asteroid.split()
    shot.kill()
    log_event("asteroid_split", radius=asteroid.radius)
```

The output files are line-delimited JSON, which makes them easy to parse with any tool, including `jq`, pandas, or another script.

> `game_state.jsonl` is already in `.gitignore`, so logs won't accidentally end up in git.

---

## Known Issues & Ideas for Improvement

These are good "next steps" if you want to extend the project:

- **No score, lives, or HUD.** Game over just prints to the terminal.
- **No sound.** Pygame has a `mixer` module; firing/explosion sounds would be a great first add-on.
- **Objects can drift forever off-screen.** Bullets and asteroids that leave the screen never get culled, which slowly leaks memory. A `kill()` call when `position` is far outside the screen bounds would fix this.
- **`AsteroidField.containers = (updatable)`** in `main.py` is technically a tuple of one element written without a trailing comma — i.e. it's just the `updatable` group, not a tuple containing it. It happens to work because `pygame.sprite.Sprite.__init__` accepts either. Writing `(updatable,)` would be more correct.
- **No restart.** Once you die you must rerun `python main.py`. A simple "press R to restart" state machine would be a nice OOP exercise.
- **No screen wrap.** Classic Asteroids wraps objects around the screen edges. Currently asteroids spawn at the edges and pass through to the other side, but the player can drive offscreen and disappear.

---

## Credits

- Built as a learning project following the spirit of the classic **Atari Asteroids (1979)**.
- Powered by the wonderful [Pygame](https://www.pygame.org/) community.
- Python tooling by [uv](https://docs.astral.sh/uv/).

Feel free to crack open `constants.py` and break things on purpose. That's how you learn.