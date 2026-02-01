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

# Vehicle types with approximate lengths
vehicles = {'Van': 6, 'Car': 4, 'Bus': 10, 'Two-wheeler': 3}

font = pygame.font.SysFont("Arial", 46, bold=True)
timer_font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 18)

# Simulate random vehicles arriving on roads
for i in range(1, random.randrange(5, 60)):
    vehicle_type = random.choice(list(vehicles.keys()))
    road_choice = random.choice(['A', 'B', 'C', 'D'])

road_thickness = 220
