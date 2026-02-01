import random
import pygame
import sys

# Initialize pygame
pygame.init()

# Lists representing vehicles on each road
road_a = []
road_b = []
road_c = []
road_d = []

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

# Simulate random vehicles arriving on roads
for i in range(1, random.randrange(5, 60)):
    vehicle_type = random.choice(list(vehicles.keys()))
    road_choice = random.choice(['A', 'B', 'C', 'D'])

road_thickness = 220
