from robodk import robolink

# Connect to RoboDK
RDK = robolink.Robolink()

robot = RDK.Item('UR3e', robolink.ITEM_TYPE_ROBOT)

if not robot.Valid():
    print("Robot 'UR3e' not found. Please check the robot name in RoboDK.")
    exit()

print(f"Connected to robot: {robot.Name()}")

robot.setSpeed(100)  # mm/s
robot.setAcceleration(50)  # mm/s²

home_position = [0, -90, 90, -90, -90, 0]
position_1 = [30, -80, 80, -90, -90, 0]
position_2 = [-30, -100, 100, -90, -90, 0]

print("Moving to home position...")
robot.MoveJ(home_position)

print("Moving to position 1...")
robot.MoveJ(position_1)

print("Moving to position 2...")
robot.MoveJ(position_2)

print("Returning to home...")
robot.MoveJ(home_position)

print("Movement complete!")

current_joints = robot.Joints()
print(f"Current joint positions (degrees): {current_joints}")
