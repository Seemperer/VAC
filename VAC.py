import random
import time
import socket

# ============================================================
# CONFIGURATION
# ============================================================
PICO_IP = "192.168.1.100"  # CHANGE THIS
PICO_PORT = 12345
SIM_DURATION = 180  # seconds

# ============================================================
# VEHICLE TYPES
# ============================================================
VEHICLES = {
    "Motorcycle": {"time": 1, "priority": 1, "type": "regular"},
    "Car": {"time": 2, "priority": 1, "type": "regular"},
    "SUV": {"time": 2, "priority": 1, "type": "regular"},
    "Van": {"time": 3, "priority": 1, "type": "regular"},
    "Truck": {"time": 4, "priority": 1, "type": "regular"},
    "Bus": {"time": 5, "priority": 1, "type": "regular"},
    "Ambulance": {"time": 2, "priority": 10, "type": "emergency"},
    "Police": {"time": 2, "priority": 10, "type": "emergency"},
    "Fire Truck": {"time": 3, "priority": 10, "type": "emergency"}
}

# Timing parameters (seconds)
MIN_GREEN = 8
MAX_GREEN = 30
EXTENSION_TIME = 3
YELLOW_TIME = 3  # <-- Yellow light duration
ALL_RED_TIME = 2
EMERGENCY_GREEN_TIME = 12

ROADS = ["North", "East", "South", "West"]
PHASES = [[0, 2], [1, 3]]  # NS, EW

# ============================================================
# INITIALISATION
# ============================================================
queues = [[] for _ in range(4)]
regular_vehicles = [v for v in VEHICLES if VEHICLES[v]["type"] == "regular"]
for _ in range(15):
    road = random.randint(0, 3)
    queues[road].append(random.choice(regular_vehicles))

signal_state = ["R"] * 4
current_phase = 0
phase_timer = 0
green_start_time = 0
is_yellow = False
is_all_red = False
phase_change_time = 0  # Track when phase changes happen


# Emergency preemption state
class EmergencyEvent:
    def __init__(self):
        self.active = False
        self.road = -1
        self.vehicle = ""
        self.start_time = 0


emergency = EmergencyEvent()
emergency_cooldown = 0


# ============================================================
# FUNCTIONS
# ============================================================
def send_command(cmd):
    """Send command to Pico W."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((PICO_IP, PICO_PORT))
        sock.sendall((cmd + "\n").encode())
        sock.close()
    except Exception as e:
        print(f"✗ Wi-Fi error: {e}")


def format_time(seconds):
    """Format time as MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def output_status(t):
    """Send signal states and display status with time."""
    cmd = f"{signal_state[0]},{signal_state[1]},{signal_state[2]},{signal_state[3]}"
    if emergency.active:
        cmd = "EMERGENCY," + cmd
    send_command(cmd)

    # Clear screen for cleaner display
    print("\033[2J\033[H", end="")

    # Header with current time
    print("=" * 80)
    print(f"🚦 4-WAY JUNCTION - VEHICLE ACTUATED CONTROL")
    print(f"⏱️  Simulation Time: {format_time(t)} / {format_time(SIM_DURATION)}")
    print("=" * 80)

    # Phase and timer info
    time_in_phase = t - phase_change_time
    if emergency.active:
        emergency_remaining = EMERGENCY_GREEN_TIME - (t - emergency.start_time)
        print(f"🚨 EMERGENCY MODE: {emergency.vehicle} on {ROADS[emergency.road]}")
        print(f"   Emergency green time remaining: {emergency_remaining:.1f}s")
    else:
        phase_name = "North-South" if current_phase == 0 else "East-West"
        if is_yellow:
            print(f"🟡 YELLOW PHASE - {phase_name}")
            print(f"   Yellow time remaining: {phase_timer:.1f}s")
        elif is_all_red:
            print(f"🔴 ALL RED CLEARANCE - Time remaining: {phase_timer:.1f}s")
        else:
            print(f"🟢 GREEN PHASE - {phase_name}")
            print(f"   Green time: {time_in_phase:.1f}s / Max: {MAX_GREEN}s")
            if time_in_phase >= MIN_GREEN:
                print(f"   Extension available: {'YES' if any(queues[r] for r in PHASES[current_phase]) else 'NO'}")

    print("-" * 80)

    # Display each road's queue with signal state
    print(f"{'ROAD':8} | {'SIGNAL':8} | {'QUEUE':8} | VEHICLES")
    print("-" * 80)

    for i, road in enumerate(ROADS):
        veh_list = queues[i]
        signal = signal_state[i]

        # Signal display with emoji
        if signal == 'G':
            signal_disp = "🟢 GREEN"
        elif signal == 'Y':
            signal_disp = "🟡 YELLOW"
        else:
            signal_disp = "🔴 RED"

        # Show emergency vehicles in queue
        veh_display = []
        for v in veh_list[:5]:  # Show first 5 vehicles
            if VEHICLES[v]["type"] == "emergency":
                emoji = "🚑" if v == "Ambulance" else "🚓" if v == "Police" else "🚒"
                veh_display.append(f"{emoji}{v}")
            else:
                veh_display.append(v)

        if len(veh_list) > 5:
            veh_display.append(f"...(+{len(veh_list) - 5})")

        veh_str = ", ".join(veh_display) if veh_display else "Empty"

        # Highlight road with emergency at front
        prefix = "🚨 " if (veh_list and VEHICLES[veh_list[0]]["type"] == "emergency") else "   "

        print(f"{prefix}{road:5} | {signal_disp:8} | {len(veh_list):5} | {veh_str}")

    print("=" * 80 + "\n")


def check_emergency():
    """Check if any road has emergency vehicle at front."""
    for r in range(4):
        if queues[r] and VEHICLES[queues[r][0]]["type"] == "emergency":
            return r, queues[r][0]
    return -1, ""


# ============================================================
# MAIN LOOP
# ============================================================
print("\n" + "=" * 80)
print("🚦 4-WAY JUNCTION - VEHICLE ACTUATED CONTROL WITH YELLOW LIGHTS")
print("=" * 80)
print(f"Pico IP: {PICO_IP}:{PICO_PORT}")
print(f"Yellow light duration: {YELLOW_TIME}s")
print(f"Min green: {MIN_GREEN}s | Max green: {MAX_GREEN}s")
print("=" * 80 + "\n")

output_status(0)
time.sleep(1)

t = 0
phase_change_time = 0

while t < SIM_DURATION:
    # --- 1. VEHICLE ARRIVALS ---
    if random.random() < 0.35:
        r = random.randint(0, 3)
        queues[r].append(random.choice(regular_vehicles))

    # --- 2. EMERGENCY VEHICLE ARRIVALS ---
    if emergency_cooldown <= 0 and random.random() < 0.05:
        r = random.randint(0, 3)
        ev = random.choice(["Ambulance", "Police", "Fire Truck"])
        queues[r].append(ev)
        emergency_cooldown = 30
        print(f"\n🎯 NEW EMERGENCY: {ev} on {ROADS[r]}!\n")
    else:
        emergency_cooldown -= 1

    # --- 3. EMERGENCY DETECTION ---
    er, ev = check_emergency()
    if not emergency.active and er != -1:
        emergency.active = True
        emergency.road = er
        emergency.vehicle = ev
        emergency.start_time = t
        if er in [0, 2]:
            current_phase = 0
        else:
            current_phase = 1
        is_yellow = False
        is_all_red = False
        phase_change_time = t
        print(f"\n🚨🚨🚨 EMERGENCY PREEMPTION! {ev} on {ROADS[er]} 🚨🚨🚨\n")
        output_status(t)

    # --- 4. VEHICLE DEPARTURES ---
    for road in PHASES[current_phase]:
        if signal_state[road] == "G" and queues[road]:
            # Simple departure: remove one vehicle per second
            # Each vehicle takes its crossing time
            if random.random() < (1.0 / VEHICLES[queues[road][0]]["time"]):
                removed = queues[road].pop(0)
                if emergency.active and emergency.road == road and VEHICLES[removed]["type"] == "emergency":
                    print(f"✅ Emergency {removed} cleared from {ROADS[road]}")

    # --- 5. TRAFFIC LIGHT CONTROL WITH YELLOW LIGHTS ---
    if emergency.active:
        # Emergency mode
        if current_phase == 0:
            signal_state = ["G", "R", "G", "R"]
        else:
            signal_state = ["R", "G", "R", "G"]

        if t - emergency.start_time >= EMERGENCY_GREEN_TIME:
            if not queues[emergency.road] or VEHICLES[queues[emergency.road][0]]["type"] != "emergency":
                emergency.active = False
                print("\n✅ Emergency preemption ended. Returning to normal.\n")
                # Start transition with yellow
                is_yellow = True
                phase_timer = YELLOW_TIME
                for r in PHASES[current_phase]:
                    signal_state[r] = "Y"
                phase_change_time = t
                output_status(t)
    else:
        # Normal actuated control WITH YELLOW LIGHTS
        current_phase_roads = PHASES[current_phase]

        # Check if we should start a new phase (all red currently)
        if all(signal_state[r] == "R" for r in current_phase_roads) and not is_yellow and not is_all_red:
            # Start green
            for r in current_phase_roads:
                signal_state[r] = "G"
            phase_timer = MIN_GREEN
            green_start_time = t
            phase_change_time = t
            is_yellow = False
            is_all_red = False
            output_status(t)

        # Handle green phase
        elif all(signal_state[r] == "G" for r in current_phase_roads):
            # Check if we need to end green
            time_in_green = t - green_start_time

            if time_in_green >= MIN_GREEN:
                vehicles_waiting = any(queues[r] for r in current_phase_roads)

                # If no vehicles waiting OR reached max green, prepare to end
                if not vehicles_waiting or time_in_green >= MAX_GREEN:
                    # Switch to yellow
                    for r in current_phase_roads:
                        signal_state[r] = "Y"
                    phase_timer = YELLOW_TIME
                    is_yellow = True
                    phase_change_time = t
                    output_status(t)

        # Handle yellow phase
        elif is_yellow:
            phase_timer -= 1
            if phase_timer <= 0:
                # Yellow finished, go to all red
                for r in current_phase_roads:
                    signal_state[r] = "R"
                phase_timer = ALL_RED_TIME
                is_yellow = False
                is_all_red = True
                phase_change_time = t
                output_status(t)

        # Handle all-red clearance
        elif is_all_red:
            phase_timer -= 1
            if phase_timer <= 0:
                # Move to next phase
                current_phase = (current_phase + 1) % 2
                is_all_red = False
                phase_change_time = t
                # Next iteration will start green

    # Slow down to real-time
    time.sleep(1)
    t += 1

print("\n" + "=" * 80)
print("🏁 SIMULATION COMPLETE")
print("=" * 80)