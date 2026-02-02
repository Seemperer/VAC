import random
import pygame
import sys

# Initialize pygame
pygame.init()

# Screen (optional, but keeps pygame happy)
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Vehicle Actuation System Simulation")

# Road types
road_types = ['Highway', 'T-junction', '+-JUNCTION']

# Lists representing vehicles on each road
road_a = []
road_b = []
road_c = []
road_d = []

# Vehicle types with approximate lengths
vehicles = {
    'Van': 6,
    'Car': 4,
    'Bus': 10,
    'Two-wheeler': 3
}

print(
    "A scenario is being created where two roads intersect each other, "
    "and a simulation on the Vehicle Actuation System will be used"
)

# Simulate random vehicles arriving on roads
for _ in range(random.randrange(5, 60)):
    vehicle_type = random.choice(list(vehicles.keys()))
    road_choice = random.choice(['A', 'B', 'C', 'D'])

    if road_choice == 'A':
        road_a.append(vehicle_type)
    elif road_choice == 'B':
        road_b.append(vehicle_type)
    elif road_choice == 'C':
        road_c.append(vehicle_type)
    else:
        road_d.append(vehicle_type)

# Print results
print("Vehicles on Road A:", road_a)
print("Vehicles on Road B:", road_b)
print("Vehicles on Road C:", road_c)
print("Vehicles on Road D:", road_d)

# Simple pygame loop (so the window doesn't close immediately)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
