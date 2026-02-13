import random
import time
import socket

# ============================================================
# CONFIGURATION
# ============================================================
PICO_IP = "192.168.1.100"  # CHANGE THIS
PICO_PORT = 12345
SIM_DURATION = 180

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

# Timing parameters
MIN_GREEN = 8
MAX_GREEN = 30
EXTENSION_TIME = 3
YELLOW_TIME = 3
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
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((PICO_IP, PICO_PORT))
        sock.sendall((cmd + "\n").encode())
        sock.close()
    except Exception as e:
        print(f"✗ Wi‑Fi error: {e}")


def output_status(t):
    cmd = f"{signal_state[0]},{signal_state[1]},{signal_state[2]},{signal_state[3]}"
    if emergency.active:
        cmd = "EMERGENCY," + cmd
    send_command(cmd)

    # Console display
    print("\033[2J\033[H", end="")
    print("=" * 70)
    print(f"🚦 4-WAY JUNCTION - VEHICLE ACTUATED CONTROL")
    print("=" * 70)
    print(f"Time: {t:.1f}s | Phase: {'NS' if current_phase == 0 else 'EW'}")
    if emergency.active:
        print(f"🚨 EMERGENCY: {emergency.vehicle} on {ROADS[emergency.road]} "
              f"({EMERGENCY_GREEN_TIME - (t - emergency.start_time):.1f}s remaining)")
    print("-" * 70)
    for i, road in enumerate(ROADS):
        veh_list = queues[i]
        signal = signal_state[i]
        sig_disp = "🟢 GREEN" if signal == 'G' else "🟡 YELLOW" if signal == 'Y' else "🔴 RED"
        prefix = "🚨" if veh_list and VEHICLES[veh_list[0]]["type"] == "emergency" else "  "
        print(f"{prefix} {road:6} | {sig_disp:12} | Queue: {len(veh_list):2} | {veh_list[:3]}")
    print("=" * 70 + "\n")


def check_emergency():
    for r in range(4):
        if queues[r] and VEHICLES[queues[r][0]]["type"] == "emergency":
            return r, queues[r][0]
    return -1, ""


# ============================================================
# MAIN LOOP
# ============================================================
print("\n" + "=" * 70)
print("🚦 4-WAY JUNCTION - EMERGENCY PREEMPTION DEMO")
print("=" * 70)
print(f"Pico IP: {PICO_IP}:{PICO_PORT}")
print("=" * 70 + "\n")

output_status(0)
time.sleep(1)

t = 0
while t < SIM_DURATION:
    # Vehicle arrivals
    if random.random() < 0.35:
        r = random.randint(0, 3)
        queues[r].append(random.choice(regular_vehicles))

    # Emergency arrival
    if emergency_cooldown <= 0 and random.random() < 0.05:
        r = random.randint(0, 3)
        ev = random.choice(["Ambulance", "Police", "Fire Truck"])
        queues[r].append(ev)
        emergency_cooldown = 30
        print(f"\n🎯 NEW EMERGENCY: {ev} on {ROADS[r]}!\n")
    else:
        emergency_cooldown -= 1

    # Emergency detection
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
        print(f"\n🚨🚨🚨 EMERGENCY PREEMPTION ACTIVATED! {ev} on {ROADS[er]} 🚨🚨🚨\n")
        output_status(t)

    # Vehicle departures
    for road in PHASES[current_phase]:
        if signal_state[road] == "G" and queues[road]:
            if random.random() < (1.0 / VEHICLES[queues[road][0]]["time"]):
                removed = queues[road].pop(0)
                if emergency.active and emergency.road == road and VEHICLES[removed]["type"] == "emergency":
                    print(f"✅ Emergency {removed} cleared from {ROADS[road]}")

    # Traffic light control
    if emergency.active:
        # Emergency mode: force green for emergency phase
        if current_phase == 0:
            signal_state = ["G", "R", "G", "R"]
        else:
            signal_state = ["R", "G", "R", "G"]

        if t - emergency.start_time >= EMERGENCY_GREEN_TIME:
            if not queues[emergency.road] or VEHICLES[queues[emergency.road][0]]["type"] != "emergency":
                emergency.active = False
                print("\n✅ Emergency preemption ended. Returning to normal.\n")
                is_yellow = True
                for r in PHASES[current_phase]:
                    signal_state[r] = "Y"
                phase_timer = YELLOW_TIME
                output_status(t)
    else:
        # Normal actuated control
        current_phase_roads = PHASES[current_phase]

        if all(signal_state[r] == "R" for r in current_phase_roads) and not is_yellow and not is_all_red:
            for r in current_phase_roads:
                signal_state[r] = "G"
            phase_timer = MIN_GREEN
            green_start_time = t
            is_yellow = False
            is_all_red = False
            output_status(t)

        elif all(signal_state[r] == "G" for r in current_phase_roads):
            phase_timer -= 1
            if t - green_start_time >= MIN_GREEN:
                vehicles_waiting = sum(len(queues[r]) for r in current_phase_roads)
                if vehicles_waiting > 0 and (t - green_start_time) < MAX_GREEN:
                    phase_timer = EXTENSION_TIME
                elif phase_timer <= 0:
                    for r in current_phase_roads:
                        signal_state[r] = "Y"
                    phase_timer = YELLOW_TIME
                    is_yellow = True
                    output_status(t)

        elif is_yellow:
            phase_timer -= 1
            if phase_timer <= 0:
                for r in current_phase_roads:
                    signal_state[r] = "R"
                phase_timer = ALL_RED_TIME
                is_yellow = False
                is_all_red = True
                output_status(t)

        elif is_all_red:
            phase_timer -= 1
            if phase_timer <= 0:
                current_phase = (current_phase + 1) % 2
                is_all_red = False

    time.sleep(1)
    t += 1

print("\n" + "=" * 70)
print("🏁 SIMULATION COMPLETE")
print("=" * 70)