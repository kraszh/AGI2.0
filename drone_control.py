import airsim
import time
import random

# Connect to the AirSim simulator
client = airsim.MultirotorClient()

# List of drone names
drones = [f"Drone{i}" for i in range(6)]
evil_drone = "Evil"
settings = {
    "SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/main/docs/settings.md",
    "SettingsVersion": 1.2,
    "SimMode": "Multirotor",

    "Vehicles": {
        "Drone0": {
          "VehicleType": "SimpleFlight",
          "X": 4, "Y": 0, "Z": -2,
      	  "Yaw": -180
        },
        "Drone1": {
          "VehicleType": "SimpleFlight",
          "X": 8, "Y": 0, "Z": -2
        },
        "Drone2": {
          "VehicleType": "SimpleFlight",
          "X": 12, "Y": 0, "Z": -2
        },
        "Drone3": {
          "VehicleType": "SimpleFlight",
          "X": 4, "Y": 4, "Z": -2
        },
        "Drone4": {
          "VehicleType": "SimpleFlight",
          "X": 8, "Y": 4, "Z": -2
        },
        "Drone5": {
          "VehicleType": "SimpleFlight",
          "X": 12, "Y": 4, "Z": -2
        },
        "Evil": {
          "VehicleType": "SimpleFlight",
          "X": 0, "Y": 0, "Z": -2
        }

    }
}
try:
    # Connect and enable API control for all drones including Evil
    for drone in drones + [evil_drone]:
        client.enableApiControl(True, drone)
        client.armDisarm(True, drone)
        print(f"Connected to {drone}")

    # Take off all drones including Evil
    print("Taking off...")
    tasks = [client.takeoffAsync(vehicle_name=drone) for drone in drones + [evil_drone]]
    for task in tasks:
        task.join()
    
    # Move regular drones to their initial positions
    print("Moving drones to initial positions...")
    tasks = [client.moveToPositionAsync(10, 10, -20, 5, vehicle_name=drone) for drone in drones]

    # Position Evil drone at a specific location
    print("Positioning Evil drone...")
    tasks.append(client.moveToPositionAsync(0, 0, -10, 5, vehicle_name=evil_drone))

    for task in tasks:
        task.join()

    print("Moving drones to new positions...")
    tasks = [client.moveToPositionAsync(3, 3, -20, 5, vehicle_name=drone) for drone in drones]

    for task in tasks:
        task.join()
    
    # Select a random drone to crash into Evil
    kamikaze_drone = random.choice(drones)
    #print(f"{kamikaze_drone} has gone rogue!")
    
    # Get Evil drone's position
    time.sleep(2)
    evil_pos = client.getMultirotorState(vehicle_name=evil_drone).kinematics_estimated.position
    #breakpoint()
    
    # Make the selected drone crash into Evil at high speed
    print(f"{kamikaze_drone} is attacking Evil!")
    kam_info = settings["Vehicles"][kamikaze_drone]
    evil_info = settings["Vehicles"][evil_drone]
    client.moveToPositionAsync(
        evil_info["X"] - kam_info["X"] + evil_pos.x_val, 
        evil_info["Y"] - kam_info["Y"] + evil_pos.y_val, 
        evil_info["Z"] - kam_info["Z"] + evil_pos.z_val,
        5,  # Higher velocity for dramatic effect
        vehicle_name=kamikaze_drone
    ).join()
    
    # Land remaining drones
    print("Landing surviving drones...")
    surviving_drones = [drone for drone in drones if drone != kamikaze_drone]
    tasks = [client.landAsync(vehicle_name=drone) for drone in surviving_drones]
    for task in tasks:
        task.join()
    
    # Disarm all drones
    for drone in drones + [evil_drone]:
        client.armDisarm(False, drone)
        client.enableApiControl(False, drone)
        
    print("Mission completed successfully!")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    
finally:
    # Ensure we disconnect properly
    for drone in drones + [evil_drone]:
        client.enableApiControl(False, drone)
