import random
import time
import socket

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
# Wi‑Fi settings for the Pico W (TCP server)
PICO_IP = "192.168.1.100"  # <-- Change to your Pico's static IP
PICO_PORT = 12345

# Simulation parameters
SIM_DURATION = 120  # seconds to run
TIME_STEP = 1.0  # seconds per simulation step

# Vehicle crossing times (seconds)
VEHICLE_TIMES = {
    "Car": 2,
    "Van": 3,
    "Bus": 5,
    "Two-wheeler": 1
}

# Actuated control parameters (seconds)
MIN_GREEN = 5
MAX_GREEN = 30
EXTENSION = 2  # extra green if vehicle detected
YELLOW_TIME = 3

# ------------------------------------------------------------
# SCENARIO DEFINITIONS
# ------------------------------------------------------------
# Each scenario defines:
# - number of roads
# - list of phases (each phase is a list of road indices that get green)
# - optional road names for display

SCENARIOS = {
    "Highway": {
        "roads": 2,
        "phases": [[0, 1]],  # both roads can be green together? No, typically highway crossing:
        # For a highway with a crossing minor road, you'd have two phases.
        # We'll assume highway = two one-way roads crossing? Actually for demo,
        # we treat as two approaches that must alternate.
        # Let's define phases: [0] then [1]
        "phase_sequence": [0, 1],
        "road_names": ["Highway Main", "Highway Cross"]
    },
    "T-junction": {
        "roads": 3,
        # roads: 0=main stem, 1=main continuing? Actually typical T: road0 (bottom), road1 (left), road2 (right)
        # phases: [0] alone, then [1,2] together (if they don't conflict)
        "phase_sequence": [[0], [1, 2]],
        "road_names": ["Main (stem)", "Side left", "Side right"]
    },
    "Plus junction": {
        "roads": 4,
        # 4-way: phases: North-South (0&2) and East-West (1&3)
        "phase_sequence": [[0, 2], [1, 3]],
        "road_names": ["North", "East", "South", "West"]
    }
}

# ------------------------------------------------------------
# INITIALISATION
# ------------------------------------------------------------
# Choose scenario
scenario_name = random.choice(list(SCENARIOS.keys()))
cfg = SCENARIOS[scenario_name]
num_roads = cfg["roads"]
phase_sequence = cfg["phase_sequence"]
road_names = cfg["road_names"]

# Create queues: each road stores a list of vehicles (strings)
queues = [[] for _ in range(num_roads)]

# Initial vehicle placement (random, not round‑robin)
for _ in range(50):
    road = random.randint(0, num_roads - 1)
    veh = random.choice(list(VEHICLE_TIMES.keys()))
    queues[road].append(veh)

# Current signal states: for each road, store colour ("R","Y","G")
signal_state = ["R"] * num_roads

# Timing variables
current_phase_index = 0
phase_timer = 0
green_start_time = 0
extensions_remaining = 0


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def total_crossing_time(queue):
    """Sum of crossing times of all vehicles currently in queue."""
    return sum(VEHICLE_TIMES[v] for v in queue)


def vehicles_present(road_indices):
    """Return True if any of the given roads have waiting vehicles."""
    for r in road_indices:
        if queues[r]:
            return True
    return False


def set_signal(road, colour):
    """Change signal for one road and return True if changed."""
    global signal_state
    if signal_state[road] != colour:
        signal_state[road] = colour
        return True
    return False


def send_command(command_str):
    """Send a command string over TCP to the Pico W."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((PICO_IP, PICO_PORT))
        sock.sendall((command_str + "\n").encode())
        sock.close()
    except Exception as e:
        print(f"[Wi‑Fi error] {e}")


def output_status(time_now):
    """Print current status and send signal states to Pico."""
    # Build a compact command string, e.g. "HW:GRN,4W:RED,TJ:YEL"
    # We'll map road index to a short code: for simplicity, use road numbers.
    # Better: use scenario prefix + road number.
    cmd_parts = []
    for i, col in enumerate(signal_state):
        # Use road index as identifier; Arduino will know mapping.
        cmd_parts.append(f"R{i}:{col}")
    cmd = ",".join(cmd_parts)
    send_command(cmd)

    # Also print human‑readable status for the user
    print(f"Time {time_now:.1f}s | Signals: {cmd}")
    for i, q in enumerate(queues):
        if q:
            print(f"   {road_names[i]}: {len(q)} vehicles")
    print("-" * 40)


# ------------------------------------------------------------
# MAIN SIMULATION LOOP
# ------------------------------------------------------------
print("\n*** VEHICLE‑ACTUATED TRAFFIC SIMULATION ***")
print(f"Scenario: {scenario_name}")
print(f"Roads: {num_roads}")
print(f"Phases: {phase_sequence}\n")

# Initial state: all red
output_status(0)
time.sleep(1)  # give time for Pico to receive

# Time loop
t = 0
while t < SIM_DURATION:
    # --- 1. VEHICLE ARRIVALS (random, every few seconds) ---
    if random.random() < 0.3:  # 30% chance per second
        road = random.randint(0, num_roads - 1)
        veh = random.choice(list(VEHICLE_TIMES.keys()))
        queues[road].append(veh)

    # --- 2. VEHICLE DEPARTURES (if green and crossing time passed) ---
    # In a real simulation we would track each vehicle's remaining time.
    # Here we simplify: if a road is green, remove one vehicle per second
    # (assuming each takes 1 sec). To respect different crossing times,
    # we would need per‑vehicle timers. For demonstration, we keep it simple:
    # remove one vehicle per second from any green road that has vehicles.
    # This is not accurate but enough to show actuation.
    for i, col in enumerate(signal_state):
        if col == "G" and queues[i]:
            queues[i].pop(0)  # remove first vehicle

    # --- 3. VEHICLE‑ACTUATED SIGNAL CONTROL ---
    # Get current phase roads
    current_phase_roads = phase_sequence[current_phase_index]

    # If currently all red (phase start), set green + start timer
    if all(signal_state[r] == "R" for r in current_phase_roads):
        for r in current_phase_roads:
            set_signal(r, "G")
        phase_timer = MIN_GREEN
        green_start_time = t
        extensions_remaining = 0  # reset
        output_status(t)

    # If in green
    elif all(signal_state[r] == "G"

              in current_phase_roads):
        # Decrement timer
        phase_timer -= TIME_STEP

        # After minimum green, check for extension
        if t - green_start_time >= MIN_GREEN:
            # If vehicles still present AND timer > 0, we are within extension period
            if vehicles_present(current_phase_roads) and (t - green_start_time) < MAX_GREEN:
                # Reset timer to EXTENSION, but don't exceed MAX_GREEN
                remaining_max = MAX_GREEN - (t - green_start_time)
                phase_timer = min(EXTENSION, remaining_max)
            else:
                # No vehicles or max green reached: prepare to change
                if phase_timer <= 0:
                    # Switch to yellow
                    for r in current_phase_roads:
                        set_signal(r, "Y")
                    phase_timer = YELLOW_TIME
                    output_status(t)

    # If in yellow
    elif all(signal_state[r] == "Y" for r in current_phase_roads):
        phase_timer -= TIME_STEP
        if phase_timer <= 0:
            # Set all to red
            for r in current_phase_roads:
                set_signal(r, "R")
            # Move to next phase
            current_phase_index = (current_phase_index + 1) % len(phase_sequence)
            # Immediately start next phase (will go green next iteration)
            # But we need to ensure a brief all‑red (clearance). We'll add a 1 sec all‑red.
            phase_timer = 1  # all‑red clearance
            output_status(t)

    # All‑red clearance
    elif all(signal_state[r] == "R" for r in current_phase_roads):
        phase_timer -= TIME_STEP
        if phase_timer <= 0:
            # Green will be set in next loop iteration (first condition)
            pass

    # --- 4. ADVANCE TIME ---
    time.sleep(TIME_STEP)  # slow down simulation to real time
    t += TIME_STEP

print("\nSimulation ended.")