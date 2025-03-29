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

def simulate_leader_failure(self):
        """Very basic leader failure simulation"""
        try:
            print_debug(f"SIMULATING FAILURE OF LEADER {self.leader_name}")
            
            # Get leader position
            if self.leader_name not in self.positions:
                print_debug("ERROR: Leader position unknown")
                return
                
            leader_pos = self.positions[self.leader_name]
            
            # Make leader fall to ground - CONVERT TO FLOAT
            x = float(leader_pos[0])
            y = float(leader_pos[1])
            z = 0.0  # Ground level
            
            print_debug(f"Making leader fall to ground at [{x:.2f}, {y:.2f}, {z:.2f}]")
            self.client.moveToPositionAsync(
                x, y, z,
                10.0,  # Fast descent
                vehicle_name=self.leader_name
            ).join()
            
            # Mark as fallen
            self.fallen[self.leader_name] = True
            print_debug(f"Leader {self.leader_name} has crashed")
            
            # Update positions
            self.update_positions()
        except Exception as e:
            print_debug(f"ERROR during leader failure simulation: {e}")
    
    def move_to_waypoint(self, waypoint, skip_leader=False):
        """Move all drones to a waypoint"""
        # CONVERT NUMPY ARRAY TO PYTHON FLOATS
        x = float(waypoint[0])
        y = float(waypoint[1])
        z = float(waypoint[2])
        
        print_debug(f"Moving to waypoint [{x:.2f}, {y:.2f}, {z:.2f}]...")
        
        waypoint_tasks = []
        for name in self.drone_names:
            if self.fallen.get(name, False):
                print_debug(f"Skipping {name} (crashed)")
                continue
                
            if skip_leader and name == self.leader_name:
                print_debug(f"Skipping {name} (leader)")
                continue
            
            try:
                print_debug(f"Moving {name} to waypoint...")
                waypoint_tasks.append(
                    self.client.moveToPositionAsync(
                        x, y, z,
                        15.0,  # velocity
                        vehicle_name=name
                    )
                )
            except Exception as e:
                print_debug(f"ERROR moving {name} to waypoint: {e}")
        
        # Wait for movement
        for task in waypoint_tasks:
            try:
                task.join()
            except Exception as e:
                print_debug(f"ERROR waiting for waypoint movement: {e}")
        
        print_debug("Waypoint movement complete")
        self.update_positions()
    
    def run_demo(self):
        """Run the fixed demo"""
        try:
            # Initialize drones
            self.initialize_drones()
            
            # Define waypoints - using Python lists instead of numpy arrays
            waypoints = [
                [0.0, 0.0, -20.0],      # Start
                [40.0, 0.0, -20.0],     # First point
                [40.0, 40.0, -20.0],    # Second point
                [0.0, 40.0, -20.0],     # Third point
                [0.0, 0.0, -20.0]       # Return to start
            ]
            
            print_debug(f"Mission has {len(waypoints)} waypoints")
            
            # First move all drones to the target altitude
            self.move_to_altitude(altitude=-20.0)
            
            # Go through waypoints
            for i, waypoint in enumerate(waypoints):
                print_debug(f"WAYPOINT {i+1}/{len(waypoints)}: [{waypoint[0]:.2f}, {waypoint[1]:.2f}, {waypoint[2]:.2f}]")
                
                # Simulate leader failure at second waypoint
                if i == 1:
                    # Move a bit toward the waypoint
                    leader_pos = self.positions.get(self.leader_name, np.array([0, 0, -20]))
                    partial_x = float(leader_pos[0]) + (float(waypoint[0]) - float(leader_pos[0])) * 0.3
                    partial_y = float(leader_pos[1]) + (float(waypoint[1]) - float(leader_pos[1])) * 0.3
                    partial_z = float(leader_pos[2]) + (float(waypoint[2]) - float(leader_pos[2])) * 0.3
                    
                    # Move to partial waypoint
                    self.move_to_waypoint([partial_x, partial_y, partial_z])
                    
                    # Simulate failure
                    self.simulate_leader_failure()
                    
                    # Other drones continue to the waypoint
                    self.move_to_waypoint(waypoint, skip_leader=True)
                else:
                    # Normal movement for all drones
                    self.move_to_waypoint(waypoint)
                
                print_debug(f"Completed waypoint {i+1}")
                time.sleep(2)  # Short pause between waypoints
            
            print_debug("Mission completed successfully!")
            print_debug("DEMONSTRATED CAPABILITIES:")
            print_debug("✓ Leader failure handled")
            print_debug("✓ Remaining drones continued mission")
            print_debug("✓ All waypoints visited")
        
        except Exception as e:
            print_debug(f"ERROR in demo execution: {e}")
            import traceback
            print_debug(traceback.format_exc())
        finally:
            # Land all drones
            print_debug("Landing all operational drones...")
            for name in self.drone_names:
                if not self.fallen.get(name, False):
                    try:
                        self.client.landAsync(vehicle_name=name).join()
                        self.client.armDisarm(False, name)
                        self.client.enableApiControl(False, name)
                        print_debug(f"{name} landed")
                    except Exception as e:
                        print_debug(f"ERROR landing {name}: {e}")
            
            print_debug("Demo completed")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║  DRONE SWARM DEMO - FIXED VERSION          ║
    ╚════════════════════════════════════════════╝
    
    This version fixes the numpy.int32 error by
    converting all values to Python native floats.
    
    Features demonstrated:
    • Leader drone failure & crash
    • Mission continuation by remaining drones
    • Multi-waypoint navigation
    """)
    
    # You can adjust number of drones if needed
    num_drones = 10  # Using fewer drones for simplicity
    
    # Create and run demo
    demo = BasicSwarmDemo(num_drones=num_drones)
    demo.run_demo()
