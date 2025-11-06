from typing import Dict, List

from robodk import robolink

# Frame names to load from RoboDK
FRAME_NAMES = [
    'Ground',
    'Table',
    'Base Frame',
    'workframe',
    'UR3e Base',
    'Block1',
    'Block2',
    'Block3',
    'Block4',
    'Gripper'
]

# Target names to load from RoboDK
TARGET_NAMES = ['Home', 'Aprox1', 'Block1', 'Close', 'Open']


def read_frames(rdk: robolink.Robolink, frame_names: List[str]) -> Dict[str, robolink.Item]:
    """
    Read all frames from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object
        frame_names: List of frame names to read

    Returns:
        Dictionary mapping frame names to frame objects
    """
    frames = {}
    print("\nReading frames...")
    for frame_name in frame_names:
        frame = rdk.Item(frame_name, robolink.ITEM_TYPE_FRAME)
        if frame.Valid():
            frames[frame_name] = frame
            pose = frame.Pose()
            print(f"✓ {frame_name}: {pose}")
        else:
            print(f"✗ {frame_name}: NOT FOUND")

    print(f"\nLoaded {len(frames)} frames")
    return frames


def read_targets(rdk: robolink.Robolink, target_names: List[str]) -> Dict[str, robolink.Item]:
    """
    Read all targets from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object
        target_names: List of target names to read

    Returns:
        Dictionary mapping target names to target objects

    Raises:
        ValueError: If a target is not found in RoboDK
    """
    targets = {}
    print("\nReading targets...")
    for target_name in target_names:
        target = rdk.Item(target_name, robolink.ITEM_TYPE_TARGET)
        if target.Valid():
            targets[target_name] = target
            print(f"✓ {target_name}: {target.Pose()}")
        else:
            print(f"✗ {target_name}: NOT FOUND")
            raise ValueError(f"Target '{target_name}' not found in RoboDK")

    print(f"\nLoaded {len(targets)} targets")
    return targets


if __name__ == '__main__':
    # Connect to RoboDK
    RDK = robolink.Robolink()

    # Get UR3e as a robot
    robot = RDK.Item('UR3e', robolink.ITEM_TYPE_ROBOT)

    if not robot.Valid():
        raise ValueError("Robot 'UR3e' not found. Please check the robot name in RoboDK.")

    print(f"Connected to robot: {robot.Name()}")

    # Load frames and targets
    frames = read_frames(RDK, FRAME_NAMES)
    targets = read_targets(RDK, TARGET_NAMES)

    # Get gripper as a robot
    gripper = RDK.Item('Zimmer HRC-03 Gripper', robolink.ITEM_TYPE_ROBOT)
    if not gripper.Valid():
        raise ValueError("Gripper 'Zimmer HRC-03 Gripper' not found")

    # === INITIALIZATION ===
    print("\n=== INITIALIZATION ===")

    # Open gripper
    print("Opening gripper...")
    gripper.MoveJ(targets['Open'])
    print("✅ Gripper opened")

    # Move robot to home
    print("Moving to Home position (from wherever the robot is)...")
    robot.setSpeedJoints(10)  # degrees/s
    robot.setAccelerationJoints(5)  # degrees/s²
    robot.MoveJ(targets['Home'])
    print("✅ Robot initialized at Home\n")

    # === TRAJECTORY SEQUENCE ===
    print("=== Starting Trajectory Sequence ===")

    # 1. Move to Aprox1 (joint movement)
    print("\n1. Moving to Aprox1 (joint movement)...")
    robot.setSpeedJoints(10)  # degrees/s
    robot.setAccelerationJoints(5)  # degrees/s²
    robot.MoveJ(targets['Aprox1'])
    print("   ✅ Reached Aprox1")

    # 2. Move to Block1 (linear movement - really slow!)
    print("\n2. Moving to Block1 (linear movement - SLOW)...")
    robot.setSpeed(10)  # mm/s - really slow!
    robot.setAcceleration(5)  # mm/s²
    robot.MoveL(targets['Block1'])
    print("   ✅ Reached Block1")

    # 3. Close gripper to grab block
    print("\n3. Closing gripper to grab block...")
    gripper.MoveJ(targets['Close'])
    print("   ✅ Gripper closed - Block grabbed")

    print("\n=== Trajectory Complete ===")
