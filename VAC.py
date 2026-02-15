import random
import time
import socket

# ============================================================
# CONFIGURATION
# ============================================================
PICO_IP = "192.168.1.100"  # CHANGE THIS to your Pico's IP
PICO_PORT = 12345
SIM_DURATION = 120  # seconds (2 minutes)

# ============================================================
# VEHICLE TYPES
# ============================================================
VEHICLE_TYPES = ["Car", "Van", "Bus", "Truck", "Motorcycle"]

# ============================================================
# INITIALISATION
# ============================================================
# Vehicle queues for each road [North, East, South, West]
queues = [[], [], [], []]
road_names = ["North", "East", "South", "West"]

# Initial vehicles: 20 vehicles distributed randomly
for _ in range(20):
    road = random.randint(0, 3)
    vehicle = random.choice(VEHICLE_TYPES)
    queues[road].append(vehicle)

print("\n" + "=" * 70)
print("🚦 4-WAY JUNCTION TRAFFIC SIMULATION")
print("=" * 70)
print(f"Pico IP: {PICO_IP}:{PICO_PORT}")
print(f"Simulation Duration: {SIM_DURATION} seconds")
print("=" * 70 + "\n")

# Connect to Pico
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((PICO_IP, PICO_PORT))
    print("✅ Connected to Pico!")
    time.sleep(1)
except Exception as e:
    print(f"❌ Failed to connect to Pico: {e}")
    print("Make sure Pico is running and IP is correct")
    exit()

# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
t = 0
while t < SIM_DURATION:

    # --- 1. RANDOM VEHICLE ARRIVALS ---
    # 30% chance per second
    if random.random() < 0.3:
        road = random.randint(0, 3)
        vehicle = random.choice(VEHICLE_TYPES)
        queues[road].append(vehicle)

    # --- 2. SEND DATA TO PICO ---
    # Format: "North,East,South,West"
    # Example: "3,5,2,4" means North:3, East:5, South:2, West:4
    data = f"{len(queues[0])},{len(queues[1])},{len(queues[2])},{len(queues[3])}"

    try:
        sock.send((data + "\n").encode())
    except:
        print("❌ Connection lost to Pico")
        break

    # --- 3. DISPLAY CURRENT STATUS ---
    # Clear screen (optional - comment out if it causes issues)
    print("\033[2J\033[H", end="")

    print("=" * 70)
    print(f"🚦 TRAFFIC SIMULATION - Time: {t:.0f}s / {SIM_DURATION}s")
    print("=" * 70)
    print("\n📊 CURRENT VEHICLE COUNTS:")
    print("-" * 70)

    for i, road in enumerate(road_names):
        count = len(queues[i])
        vehicles = queues[i][:5]  # Show first 5 vehicles
        vehicles_str = ", ".join(vehicles) if vehicles else "Empty"
        if len(queues[i]) > 5:
            vehicles_str += f" ... and {len(queues[i]) - 5} more"

        # Bar graph visualization
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        print(f"{road:6} | {count:2} vehicles | {bar} | {vehicles_str}")

    print("-" * 70)
    print(f"📤 Sent to Pico: {data}")
    print("=" * 70)

    # Slow down to real-time
    time.sleep(1)
    t += 1

print("\n" + "=" * 70)
print("🏁 SIMULATION COMPLETE")
print("=" * 70)
sock.close()