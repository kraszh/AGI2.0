import airsim
import numpy as np
import time
import datetime
import sys

def print_debug(msg):
    """Print debug message with timestamp"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")
    # Force immediate printing
    sys.stdout.flush()

class BasicSwarmDemo:
    """
    Fixed drone swarm demo that converts numpy values to Python native types
    """
    def __init__(self, num_drones=5):
        print("="*80)
        print("DRONE SWARM DEMO - FIXED VERSION")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print_debug("Connecting to AirSim...")
        try:
            self.client = airsim.MultirotorClient()
            self.client.confirmConnection()
            print_debug("✓ Connection established")
        except Exception as e:
            print_debug(f"ERROR connecting to AirSim: {e}")
            raise
        
        self.num_drones = num_drones
        self.drone_names = [f"Drone{i+1}" for i in range(num_drones)]
        self.leader_name = "Drone3"
        
        # Simple tracking
        self.positions = {}
        self.fallen = {name: False for name in self.drone_names}
        
        print_debug(f"Initialized with {num_drones} drones")
    
    def initialize_drones(self):
        """Basic drone initialization"""
        print_debug("Initializing drones...")
        
        for name in self.drone_names:
            try:
                print_debug(f"Enabling API control for {name}...")
                self.client.enableApiControl(True, name)
                self.client.armDisarm(True, name)
                print_debug(f"✓ {name} initialized")
            except Exception as e:
                print_debug(f"ERROR initializing {name}: {e}")
                raise
        
        # Basic takeoff
        print_debug("Executing takeoff...")
        takeoff_tasks = []
        for name in self.drone_names:
            try:
                takeoff_tasks.append(self.client.takeoffAsync(vehicle_name=name))
                print_debug(f"- {name} takeoff initiated")
            except Exception as e:
                print_debug(f"ERROR in takeoff for {name}: {e}")
        
        # Wait for takeoff
        for task in takeoff_tasks:
            try:
                task.join()
            except Exception as e:
                print_debug(f"ERROR waiting for takeoff: {e}")
        
        print_debug("All drones should be airborne")
        
        # Update positions
        self.update_positions()
    
    def update_positions(self):
        """Update position data"""
        for name in self.drone_names:
            if self.fallen.get(name, False):
                continue
                
            try:
                state = self.client.getMultirotorState(vehicle_name=name)
                pos = state.kinematics_estimated.position
                self.positions[name] = np.array([pos.x_val, pos.y_val, pos.z_val])
                print_debug(f"{name} position: [{pos.x_val:.2f}, {pos.y_val:.2f}, {pos.z_val:.2f}]")
            except Exception as e:
                print_debug(f"ERROR getting position for {name}: {e}")
    
    def move_to_altitude(self, altitude=-20):
        """Move all drones to the same altitude first"""
        print_debug(f"Moving all drones to altitude {altitude}...")
        
        altitude_tasks = []
        for name in self.drone_names:
            if self.fallen.get(name, False):
                continue
                
            try:
                # Get current position
                current_pos = self.positions.get(name, np.array([0, 0, 0]))
                
                # Create new position at desired altitude - CONVERT TO FLOAT
                x = float(current_pos[0])
                y = float(current_pos[1])
                z = float(altitude)  # Convert to Python float
                
                print_debug(f"Moving {name} to altitude {altitude}...")
                altitude_tasks.append(
                    self.client.moveToPositionAsync(
                        x, y, z,
                        5.0,  # velocity
                        vehicle_name=name
                    )
                )
            except Exception as e:
                print_debug(f"ERROR moving {name} to altitude: {e}")
        
        # Wait for altitude adjustment
        for task in altitude_tasks:
            try:
                task.join()
            except Exception as e:
                print_debug(f"ERROR waiting for altitude adjustment: {e}")
        
        print_debug("All drones should be at target altitude")
        self.update_positions()
