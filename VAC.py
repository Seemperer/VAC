import random
import time

# -------------------- JUNCTION TYPES --------------------
junctions = {
    "Highway": 2,
    "T-junction": 3,
    "Plus junction": 4
}

junction_type = random.choice(list(junctions.keys()))
roads_count = junctions[junction_type]

# -------------------- VEHICLE TYPES --------------------
vehicles = {
    "Car": 4,
    "Van": 6,
    "Bus": 10,
    "Two-wheeler": 3
}

TOTAL_VEHICLES = 50

# -------------------- CREATE ROADS --------------------
roads = []

for i in range(roads_count):
    roads.append([])

for i in range(TOTAL_VEHICLES):
    road_number = i % roads_count
    vehicle_name = random.choice(list(vehicles.keys()))
    crossing_time = vehicles[vehicle_name] * 0.5

    roads[road_number].append((vehicle_name, crossing_time))

# -------------------- SIGNAL TIME CALCULATION --------------------
signal_times = []
total_vehicles = TOTAL_VEHICLES

for road in roads:
    traffic_ratio = len(road) / total_vehicles
    green_time = round(traffic_ratio * 40, 2)

    if green_time < 5:
        green_time = 5

    signal_times.append(green_time)

# -------------------- PRINT DETAILS --------------------
print("\nVEHICLE ACTUATION SYSTEM SIMULATION")
print("----------------------------------")
print("Junction Type:", junction_type)
print("Number of Roads:", roads_count)
print("Total Vehicles:", TOTAL_VEHICLES)
print()

for i in range(roads_count):
    print("Road", i + 1, "has", len(roads[i]), "vehicles")

print("\nGreen Signal Time (seconds):")
for i in range(roads_count):
    print("Road", i + 1, ":", signal_times[i])

# -------------------- SIMULATION --------------------
print("\nStarting Simulation...\n")

for cycle in range(2):
    print("Signal Cycle", cycle + 1)

    for i in range(roads_count):
        print("\nGREEN signal for Road", i + 1)
        print("Signal Time:", signal_times[i], "seconds")

        total_time = 0
        for vehicle in roads[i]:
            print("Vehicle:", vehicle[0], "| Crossing Time:", vehicle[1], "seconds")
            total_time += vehicle[1]

        print("Total crossing time:", round(total_time, 2), "seconds")
        time.sleep(1)

print("\nSimulation Finished.")
