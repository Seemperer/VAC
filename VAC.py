import random
import pygame
import sys
import time

pygame.init()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Signal (No Green-Time Inflation)")
clock = pygame.time.Clock()

# Colors
GRASS = (34, 139, 34)
ROAD = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 70, 70)
GREEN = (70, 255, 70)
ORANGE = (255, 165, 0)

font = pygame.font.SysFont("Arial", 46, bold=True)
timer_font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 18)

road_thickness = 220

# =========================
# TRAFFIC DATA
# =========================
roads = {
    "A": {"active": [], "incoming": []},
    "B": {"active": [], "incoming": []},
    "C": {"active": [], "incoming": []},
    "D": {"active": [], "incoming": []}
}

vehicles = {
    "Van": 6,
    "Car": 4,
    "Bus": 10,
    "Two-wheeler": 3,
    "Ambulance": 2,
    "Police": 2
}

EMERGENCY = {"Ambulance", "Police"}
MAX_VEHICLES = 50

# =========================
# SIGNAL STATE
# =========================
current_road = None
current_timer = 0
signal_active = False
last_tick = time.time()

# =========================
# VEHICLE SPAWNING
# =========================
next_spawn = time.time()
SPAWN_MIN, SPAWN_MAX = 0.4, 1.2

# =========================
# LOGIC FUNCTIONS
# =========================
def road_load(r):
    return sum(vehicles[v] for v in roads[r]["active"])

def has_emergency(r):
    return any(v in EMERGENCY for v in roads[r]["active"])

def choose_next_road():
    for r in roads:
        if has_emergency(r):
            return r
    return max(roads, key=lambda r: road_load(r))

def start_signal(r):
    global current_road, current_timer, signal_active
    current_road = r
    current_timer = road_load(r)
    signal_active = True

def merge_queues(r):
    roads[r]["active"].extend(roads[r]["incoming"])
    roads[r]["incoming"].clear()

def add_vehicle(r, v):
    if signal_active and r == current_road:
        roads[r]["incoming"].append(v)
    else:
        roads[r]["active"].append(v)

def remove_vehicle(r):
    for i, v in enumerate(roads[r]["active"]):
        if v in EMERGENCY:
            roads[r]["active"].pop(i)
            return
    if roads[r]["active"]:
        roads[r]["active"].pop(0)

# =========================
# DRAWING
# =========================
def draw_scene():
    screen.fill(GRASS)
    cx, cy = WIDTH // 2, HEIGHT // 2

    pygame.draw.rect(screen, ROAD, (cx - road_thickness//2, 0, road_thickness, HEIGHT))
    pygame.draw.rect(screen, ROAD, (0, cy - road_thickness//2, WIDTH, road_thickness))

    positions = {
        "A": (cx, 40),
        "B": (WIDTH - 60, cy),
        "C": (cx, HEIGHT - 60),
        "D": (40, cy)
    }

    for r, (x, y) in positions.items():
        color = ORANGE if has_emergency(r) else GREEN if r == current_road else WHITE
        label = font.render(r, True, color)
        screen.blit(label, label.get_rect(center=(x, y)))

        time_text = current_timer if r == current_road else road_load(r)
        timer = timer_font.render(f"{time_text}s", True, GREEN if r == current_road else RED)
        screen.blit(timer, timer.get_rect(center=(x, y + 40)))

    info = small_font.render(
        f"A:{len(roads['A']['active'])}+{len(roads['A']['incoming'])}  "
        f"B:{len(roads['B']['active'])}+{len(roads['B']['incoming'])}  "
        f"C:{len(roads['C']['active'])}+{len(roads['C']['incoming'])}  "
        f"D:{len(roads['D']['active'])}+{len(roads['D']['incoming'])}",
        True, (0, 0, 0)
    )
    screen.blit(info, (10, HEIGHT - 25))

# =========================
# MAIN LOOP
# =========================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    now = time.time()

    # 🚗 Spawn vehicles
    if now >= next_spawn:
        road = random.choice(list(roads.keys()))
        if len(roads[road]["active"]) + len(roads[road]["incoming"]) < MAX_VEHICLES:
            if random.random() < 0.05:
                add_vehicle(road, random.choice(list(EMERGENCY)))
            else:
                add_vehicle(road, random.choice(
                    [v for v in vehicles if v not in EMERGENCY]
                ))
        next_spawn = now + random.uniform(SPAWN_MIN, SPAWN_MAX)

    # 🚦 Signal control
    if not signal_active:
        start_signal(choose_next_road())
        last_tick = now

    # ⏱ Countdown
    if signal_active and now - last_tick >= 1:
        current_timer -= 1
        last_tick = now

        remove_vehicle(current_road)

        if current_timer <= 0:
            merge_queues(current_road)
            signal_active = False

    draw_scene()
    pygame.display.flip()
    clock.tick(60)
