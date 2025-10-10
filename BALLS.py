from picographics import PicoGraphics, DISPLAY_TUFTY_2040
import time
import random
from pimoroni import Button
from math import sin

# --- Configuration ---
FRAME_DELAY_MS = 20
FRAME_DELAY_S = FRAME_DELAY_MS / 1000.0

# --- Setup Display & Hardware (Tufty 2040) ---
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
display.set_backlight(1.0)
display.set_font("bitmap8")

WIDTH, HEIGHT = display.get_bounds()

# --- Button Initialization (Tufty 2040 Pinout) ---
# New button assignments:
# UP (Pin 22): Add 1 ball
# DOWN (Pin 6): Remove 1 ball
# LEFT/A (Pin 7): Remove ALL balls
# RIGHT/C (Pin 9): Add 100 balls
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)
button_left = Button(7, invert=False)
button_right = Button(9, invert=False)
button_shoot = Button(8, invert=False) # B button (now unused for control)

# --- Define Colors (Pens) ---
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
TITLE_COLOR = display.create_pen(150, 200, 255)
BALL_PENS = []

# Generate a set of colorful pens (all shades of purple)
def generate_pens():
    global BALL_PENS
    # Nice shades of purple and related colors
    colors = [
        (102, 0, 153),   # Deep Violet
        (147, 112, 219), # Medium Purple
        (180, 150, 255), # Lavender (lighter, brighter)
        (255, 0, 255),   # Magenta (brightest)
        (75, 0, 130),    # Indigo (dark)
        (85, 40, 115),   # Grape (muted)
    ]
    for r, g, b in colors:
        BALL_PENS.append(display.create_pen(r, g, b))

generate_pens()


# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius, vx, vy, pen):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.pen = pen
        self.dampening = 0.95  # Energy loss on bounce

    def update(self):
        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # --- Boundary Collision (Reversal) ---

        # Left/Right walls
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -self.dampening
            # Snap to boundary to prevent sticking
            if self.x - self.radius < 0:
                self.x = self.radius
            else:
                self.x = WIDTH - self.radius

        # Top/Bottom walls
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -self.dampening
            # Snap to boundary
            if self.y - self.radius < 0:
                self.y = self.radius
            else:
                self.y = HEIGHT - self.radius

    def draw(self):
        display.set_pen(self.pen)
        display.circle(int(self.x), int(self.y), self.radius)

# --- Game State ---
balls = []
last_press_time = 0.0
DEBOUNCE_TIME = 0.2  # Seconds

def add_ball():
    """Adds a new ball with random properties to the center of the screen."""
    radius = random.randint(5, 15)
    
    # Random velocity: -5 to 5, avoiding zero to ensure movement
    vx = random.uniform(-4, 4)
    if abs(vx) < 1: vx = 1.0 if vx >= 0 else -1.0
    
    vy = random.uniform(-4, 4)
    if abs(vy) < 1: vy = 1.0 if vy >= 0 else -1.0
    
    # Start position is the center
    x = WIDTH // 2
    y = HEIGHT // 2
    
    # Select a random color pen
    pen = random.choice(BALL_PENS)
    
    balls.append(Ball(x, y, radius, vx, vy, pen))

def remove_ball():
    """Removes the last added ball from the list, if any exist."""
    if balls:
        balls.pop()

def remove_all_balls():
    """Removes all balls from the screen."""
    global balls
    balls = []

def add_multiple_balls(count):
    """Adds a specified number of balls to the screen."""
    # Note: Adding 100 at once might cause performance slowdown on the Tufty!
    for _ in range(count):
        add_ball()

# Add initial balls
add_multiple_balls(3)

# --- Main Game Loop ---
def run_game():
    global last_press_time
    
    while True:
        current_time = time.ticks_ms() / 1000.0
        
        # 1. Input Handling: New controls for adding and removing balls
        if (current_time - last_press_time) > DEBOUNCE_TIME:
            if button_up.is_pressed:
                add_ball()
                last_press_time = current_time
            elif button_down.is_pressed:
                remove_ball()
                last_press_time = current_time
            elif button_left.is_pressed: # A Button: Remove All
                remove_all_balls()
                last_press_time = current_time
            elif button_right.is_pressed: # C Button: Add 100
                add_multiple_balls(100)
                last_press_time = current_time

        # 2. Clear screen
        display.set_pen(BLACK)
        display.clear()
        
        # 3. Draw Title and Info
        display.set_pen(TITLE_COLOR)
        # Display the new controls
        display.text("UP/DOWN: +/- 1", 5, 5, scale=2)
        display.text("A: Clear | C: +100", 5, 20, scale=2)
        display.text(f"COUNT: {len(balls)}", 5, HEIGHT - 15, scale=2)

        # 4. Update and Draw Balls
        for ball in balls:
            ball.update()
            ball.draw()

        # 5. Push buffer and wait
        display.update()
        time.sleep(FRAME_DELAY_S)

# Start the game
try:
    run_game()
except KeyboardInterrupt:
    print("Game stopped.")
