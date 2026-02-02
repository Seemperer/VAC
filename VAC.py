import pygame
import random
import sys

# -------------------- INITIAL SETUP --------------------
pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle Actuation System Simulation")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 28)

# -------------------- CONSTANTS --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)

# Vehicle types: length also affects crossing time
VEHICLES = {
    "Car": 4,
    "Van": 6,
    "Bus": 10,
    "Two-wheeler": 3
}

SPEED = 2
TOTAL_VEHICLES = 50

# -------------------- ROAD CONFIG --------------------
road_types = {
    "Highway": 2,
    "T-junction": 3,
    "Plus junction": 4
}

junction_type = random.choice(list(road_types.keys()))
ROAD_COUNT = road_types[junction_type]

# -------------------- VEHICLE CLASS --------------------
class Vehicle:
    def __init__(self, x, y, direction, vtype):
        self.x = x
        self.y = y
        self.direction = direction
        self.type = vtype
        self.length = VEHICLES[vtype]
        self.cross_time = self.length * 0.5  # time based on size

    def move(self):
        if self.direction == "right":
            self.x += SPEED
        elif self.direction == "left":
            self.x -= SPEED
        elif self.direction == "down":
            self.y += SPEED
        elif self.direction == "up":
            self.y -= SPEED

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, 20, 10))

# -------------------- CREATE ROADS --------------------
roads = [[] for _ in range(ROAD_COUNT)]
directions = ["right", "left", "down", "up"]

for i in range(TOTAL_VEHICLES):
    road_index = i % ROAD_COUNT
    direction = directions[road_index]
    vtype = random.choice(list(VEHICLES.keys()))

    if direction == "right":
        vehicle = Vehicle(0, 350, direction, vtype)
    elif direction == "left":
        vehicle = Vehicle(WIDTH, 320, direction, vtype)
    elif direction == "down":
        vehicle = Vehicle(420, 0, direction, vtype)
    else:
        vehicle = Vehicle(450, HEIGHT, direction, vtype)

    roads[road_index].append(vehicle)

# -------------------- SIGNAL TIMING --------------------
def calculate_signal_times():
    times = []
    total = sum(len(r) for r in roads)

    for road in roads:
        proportion = len(road) / total
        times.append(max(5, int(proportion * 40)))

    return times

signal_times = calculate_signal_times()
current_road = 0
signal_timer = signal_times[current_road]

# -------------------- MAIN LOOP --------------------
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw roads
    pygame.draw.rect(screen, GRAY, (0, 300, WIDTH, 80))
    pygame.draw.rect(screen, GRAY, (400, 0, 80, HEIGHT))

    # Signal logic
    signal_timer -= 1 / 60
    if signal_timer <= 0:
        current_road = (current_road + 1) % ROAD_COUNT
        signal_timer = signal_times[current_road]

    # Draw signal status
    for i in range(ROAD_COUNT):
        color = GREEN if i == current_road else RED
        pygame.draw.circle(screen, color, (50 + i * 50, 50), 12)

    # Move vehicles
    for i, road in enumerate(roads):
        for v in road:
            if i == current_road:
                v.move()
            v.draw()

    # Info text
    info = FONT.render(f"Junction: {junction_type}", True, BLACK)
    screen.blit(info, (10, HEIGHT - 40))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
