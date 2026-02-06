import random

# choose road type
road_type = random.choice(["Highway", "T-junction", "Plus junction"])

# number of roads
if road_type == "Highway":
    roads_count = 2
elif road_type == "T-junction":
    roads_count = 3
else:
    roads_count = 4

# vehicle times
vehicle_time = {
    "Car": 2,
    "Van": 3,
    "Bus": 5,
    "Two-wheeler": 1
}

# create roads
roads = []
for i in range(roads_count):
    roads.append([])

# add 50 vehicles
for i in range(50):
    road_no = i % roads_count
    v = random.choice(list(vehicle_time.keys()))
    roads[road_no].append(v)

# show basic info
print("\nTRAFFIC SIGNAL SIMULATION")
print("Road Type:", road_type)
print("Number of Roads:", roads_count)
print("Total Vehicles: 50\n")

# show vehicles on each road
for i in range(roads_count):
    print("Road", i + 1, "vehicles:", len(roads[i]))

print("\nSignal Time for Each Road:")

# calculate and print signal time
for i in range(roads_count):
    signal_time = (len(roads[i]) / 50) * 60
    if signal_time < 5:
        signal_time = 5
    print("Road", i + 1, ":", round(signal_time, 2), "seconds")

print("\nVehicle crossing time:")

# show vehicle times
for i in range(roads_count):
    print("Road", i + 1)
    for v in roads[i]:
        print(" ", v, "takes", vehicle_time[v], "seconds")
