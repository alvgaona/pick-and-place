from typing import Dict, List
from robodk import robolink, robomath
from time import sleep

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
    'Gripper',
]

# Target names to load from RoboDK
TARGET_NAMES = ['Home', 'Aprox1', 'Block1', 'Obj1', 'Close', 'Open']


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


def read_blocks(rdk: robolink.Robolink) -> Dict[str, robolink.Item]:
    """
    Read all blocks from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object

    Returns:
        Dictionary mapping block names to block objects

    Raises:
        ValueError: If a block is not found in RoboDK
    """
    blocks = {}
    print("\nReading blocks...")
    blocks = {
        "Block1": rdk.Item("_PIEZA_Bloque20x30x20"),
        "Block2": rdk.Item("_PIEZA_Bloque20x30x10"),
        "Block3": rdk.Item("_PIEZA_Bloque20x30x40"),
        "Block4": rdk.Item("_PIEZA_Bloque20x30x30"),
    }
    print(f"\nLoaded {len(blocks)} blocks")
    return blocks


def reset_blocks(
    blocks: Dict[str, robolink.Item],
    frames: Dict[str, robolink.Item],
    blockPoses: Dict[str, robomath.Mat],
):
    print("\nResetting block positions...")
    for name in blocks.keys():
        blocks[name].setParent(frames[name])
        blocks[name].setPoseAbs(blockPoses[name])
    print("✅ Block positions reset")


if __name__ == "__main__":
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
    blocks = read_blocks(RDK)
    blockPoses = {name: blocks[name].PoseAbs() for name in blocks.keys()}

    # Get gripper as a robot
    gripper = RDK.Item('Zimmer HRC-03 Gripper', robolink.ITEM_TYPE_ROBOT)
    if not gripper.Valid():
        raise ValueError("Gripper 'Zimmer HRC-03 Gripper' not found")

    # Get TCP
    tcp = RDK.Item("Tool 1", robolink.ITEM_TYPE_TOOL)
    if not gripper.Valid():
        raise ValueError("TCP not found")

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

    robot.setPoseFrame(frames['Block1'])

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
    print("   ✅ Gripper closed")

    # 4. Attach block to gripper
    print("\n4. Attaching object...")
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print("   ✅ Block grabbed")

    # 5. Move to Obj1 (joint movement)
    print("\n5. Moving to Obj1 (joint movement)...")
    robot.setSpeedJoints(10)  # degrees/s
    robot.setAccelerationJoints(5)  # degrees/s²
    robot.setPoseFrame(frames["workframe"])
    robot.MoveJ(targets['Obj1'])
    print("   ✅ Reached Obj1")

    # 6. Open gripper to release block
    print("\n6. Opening gripper to release block...")
    gripper.MoveJ(targets['Open'])
    print("   ✅ Gripper opened")

    # 7. Detach block to gripper
    print("\n7. Detaching object...")
    tcp.DetachAll(frames['workframe'])
    print("   ✅ Block released")
    
    # 8. Move to Aprox1 (joint movement)
    robot.setPoseFrame(frames['Block1'])
    print("\n8. Moving to Aprox1 (joint movement)...")
    robot.setSpeedJoints(10)  # degrees/s
    robot.setAccelerationJoints(5)  # degrees/s²
    robot.MoveJ(targets['Aprox1'])
    print("   ✅ Reached Aprox1")

    print("\n=== Trajectory Complete ===")
    sleep(3)
    reset_blocks(blocks, frames, blockPoses)
