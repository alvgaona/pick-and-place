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
    'Block1 Targets',
    'Block2 Targets',
    'Block3 Targets',
    'Block4 Targets',
    'Gripper',
]

# Target names to load from RoboDK
TARGET_NAMES = [
    'Home', 'Close', 'Open',
    'Target Blue', 'Target Blue 2', 'Target Blue 3', 'Target Blue 4',
    'Target Green', 'Target Green 2', 'Target Green 3', 'Target Green 4',
    'Target Green 5', 'Target Green 6',
    'Target Red', 'Target Red 2', 'Target Red 3', 'Target Red 4',
    'Target Yellow', 'Target Yellow 2', 'Target Yellow 3', 'Target Yellow 4',
]


def read_frames(rdk: robolink.Robolink, frame_names: List[str]) -> Dict[str, robolink.Item]:
    '''
    Read all frames from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object
        frame_names: List of frame names to read

    Returns:
        Dictionary mapping frame names to frame objects
    '''
    frames = {}
    print('\nReading frames...')
    for frame_name in frame_names:
        frame = rdk.Item(frame_name, robolink.ITEM_TYPE_FRAME)
        if frame.Valid():
            frames[frame_name] = frame
            pose = frame.Pose()
            print(f'✓ {frame_name}: {pose}')
        else:
            print(f'✗ {frame_name}: NOT FOUND')

    print(f'\nLoaded {len(frames)} frames')
    return frames


def read_targets(rdk: robolink.Robolink, target_names: List[str]) -> Dict[str, robolink.Item]:
    '''
    Read all targets from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object
        target_names: List of target names to read

    Returns:
        Dictionary mapping target names to target objects

    Raises:
        ValueError: If a target is not found in RoboDK
    '''
    targets = {}
    print('\nReading targets...')
    for target_name in target_names:
        target = rdk.Item(target_name, robolink.ITEM_TYPE_TARGET)
        if target.Valid():
            targets[target_name] = target
            print(f'✓ {target_name}: {target.Pose()}')
        else:
            print(f'✗ {target_name}: NOT FOUND')
            raise ValueError(f'Target \'{target_name}\' not found in RoboDK')

    print(f'\nLoaded {len(targets)} targets')
    return targets


def read_blocks(rdk: robolink.Robolink) -> Dict[str, robolink.Item]:
    '''
    Read all blocks from RoboDK and store them in a dictionary.

    Args:
        rdk: RoboDK connection object

    Returns:
        Dictionary mapping block names to block objects

    Raises:
        ValueError: If a block is not found in RoboDK
    '''
    blocks = {}
    print('\nReading blocks...')
    blocks = {
        'Block1': rdk.Item('_PIEZA_Bloque20x30x20'),
        'Block2': rdk.Item('_PIEZA_Bloque20x30x10'),
        'Block3': rdk.Item('_PIEZA_Bloque20x30x40'),
        'Block4': rdk.Item('_PIEZA_Bloque20x30x30'),
    }
    print(f'\nLoaded {len(blocks)} blocks')
    return blocks


def reset_blocks(
    blocks: Dict[str, robolink.Item],
    frames: Dict[str, robolink.Item],
    blockPoses: Dict[str, robomath.Mat],
):
    print('\nResetting block positions...')
    for name in blocks.keys():
        blocks[name].setParent(frames[name])
        blocks[name].setPoseAbs(blockPoses[name])
    print('✅ Block positions reset')


if __name__ == '__main__':
    # Connect to RoboDK
    RDK = robolink.Robolink()

    # Get UR3e as a robot
    robot = RDK.Item('UR3e', robolink.ITEM_TYPE_ROBOT)

    if not robot.Valid():
        raise ValueError('Robot \'UR3e\' not found. Please check the robot name in RoboDK.')

    print(f'Connected to robot: {robot.Name()}')

    # Load frames and targets
    frames = read_frames(RDK, FRAME_NAMES)
    targets = read_targets(RDK, TARGET_NAMES)
    blocks = read_blocks(RDK)
    blockPoses = {name: blocks[name].PoseAbs() for name in blocks.keys()}

    # Get gripper as a robot
    gripper = RDK.Item('Zimmer HRC-03 Gripper', robolink.ITEM_TYPE_ROBOT)
    if not gripper.Valid():
        raise ValueError('Gripper \'Zimmer HRC-03 Gripper\' not found')

    # Get TCP
    tcp = RDK.Item('Tool 1', robolink.ITEM_TYPE_TOOL)
    if not gripper.Valid():
        raise ValueError('TCP not found')

     # === INITIALIZATION ===
    print('\n=== INITIALIZATION ===')

    reset_blocks(blocks, frames, blockPoses)

    # Open gripper
    print('Opening gripper...')
    gripper.MoveJ(targets['Open'])
    print('✅ Gripper opened')

    # Move robot to home
    print('Moving to Home position (from wherever the robot is)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveJ(targets['Home'])
    print('✅ Robot initialized at Home\n')

    # === TRAJECTORY SEQUENCE BLUE ===
    print('=== Starting Trajectory Sequence ===')

    robot.setPoseFrame(frames['Block2 Targets'])

    # 1. Move to Target Blue (joint movement)
    print('\n1. Moving to Target Blue (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveJ(targets['Target Blue'])
    print('   ✅ Reached Target Blue')

    # 2. Move to Block1 (linear movement - really slow!)
    print('\n2. Moving to Target Blue 2 (linear movement - SLOW)...')
    robot.setSpeed(30)  # mm/s - really slow!
    robot.setAcceleration(20)  # mm/s²
    robot.MoveL(targets['Target Blue 2'])
    print('   ✅ Reached Target Blue 2')

    # 3. Close gripper to grab block
    print('\n3. Closing gripper to grab block...')
    gripper.MoveJ(targets['Close'])
    print('   ✅ Gripper closed')

    # 4. Attach block to gripper
    print('\n4. Attaching object...')
    robot.setPoseFrame(frames['Block2'])
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print('   ✅ Block grabbed')

    # 5. Move to Target Blue (joint movement)
    print('\n5. Moving to Target Blue (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block2 Targets'])
    robot.MoveL(targets['Target Blue'])
    print('   ✅ Reached Blue')

    # 6. Move to Target Blue 3 (joint movement)
    print('\n5. Moving to Target Blue 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block2 Targets'])
    robot.MoveL(targets['Target Blue 3'])
    print('   ✅ Reached Blue')

    # 7. Move to Target Blue 4 (joint movement)
    print('\n5. Moving to Target Blue 4 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block2 Targets'])
    robot.MoveL(targets['Target Blue 4'])
    print('   ✅ Reached Blue')

    # 8. Open gripper to release block
    print('\n6. Opening gripper to release block...')
    gripper.MoveJ(targets['Open'])
    print('   ✅ Gripper opened')

    # 9. Detach block to gripper
    print('\n7. Detaching object...')
    robot.setPoseFrame(frames['Block2'])
    tcp.DetachAll(frames['Block2'])
    print('   ✅ Block released')

    # 10. Move to Aprox1 (joint movement)
    robot.setPoseFrame(frames['Block2 Targets'])
    print('\n8. Moving to Aprox1 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveJ(targets['Target Blue 3'])
    print('   ✅ Reached Target Blue 3')

    # === TRAJECTORY SEQUENCE GREEN ===
    print('=== Starting Trajectory Sequence ===')

    robot.setPoseFrame(frames['Block1 Targets'])

    # 1. Move to Target Green (joint movement)
    print('\n1. Moving to Target Green (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveL(targets['Target Green'])
    print('   ✅ Reached Target Green')

    # 2. Move to Green (linear movement - really slow!)
    print('\n2. Moving to Target Green 2 (linear movement - SLOW)...')
    robot.setSpeed(30)  # mm/s - really slow!
    robot.setAcceleration(20)  # mm/s²
    robot.MoveL(targets['Target Green 2'])
    print('   ✅ Reached Target Green 2')

    # 3. Close gripper to grab block
    print('\n3. Closing gripper to grab block...')
    gripper.MoveJ(targets['Close'])
    print('   ✅ Gripper closed')

    # 4. Attach block to gripper
    print('\n4. Attaching object...')
    robot.setPoseFrame(frames['Block1'])
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print('   ✅ Block grabbed')

    # 5. Move to Target Green 2 (joint movement)
    print('\n5. Moving to Target Green (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green'])

    print('   ✅ Reached Green')

    # 6. Move to Target Green 3 (joint movement)
    print('\n5. Moving to Target Green 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 3'])
    print('   ✅ Reached Green')

    # 7. Move to Target Green 4 (joint movement)
    print('\n5. Moving to Target Green 4 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 4'])
    print('   ✅ Reached Green')

    # 8. Open gripper to release block
    print('\n6. Opening gripper to release block...')
    gripper.MoveJ(targets['Open'])
    print('   ✅ Gripper opened')

    # 9. Detach block to gripper
    print('\n7. Detaching object...')
    robot.setPoseFrame(frames['Block1'])
    tcp.DetachAll(frames['Block1'])
    print('   ✅ Block released')

    # 10. Move to Green (joint movement)
    print('\n8. Moving to Green (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 3'])
    print('   ✅ Reached Target Green 3')

    # === TRAJECTORY SEQUENCE YELLOW ===
    print('=== Starting Trajectory Sequence ===')

    robot.setPoseFrame(frames['Block4 Targets'])

    # 1. Move to Target Yellow (joint movement)
    print('\n1. Moving to Target Yellow (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveL(targets['Target Yellow'])
    print('   ✅ Reached Target Yellow')

    # 2. Move to Yellow (linear movement - really slow!)
    print('\n2. Moving to Target Yellow 2 (linear movement - SLOW)...')
    robot.setSpeed(30)  # mm/s - really slow!
    robot.setAcceleration(20)  # mm/s²
    robot.MoveL(targets['Target Yellow 2'])
    print('   ✅ Reached Target Yellow 2')

    # 3. Close gripper to grab block
    print('\n3. Closing gripper to grab block...')
    gripper.MoveJ(targets['Close'])
    print('   ✅ Gripper closed')

    # 4. Attach block to gripper
    print('\n4. Attaching object...')
    robot.setPoseFrame(frames['Block4'])
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print('   ✅ Block grabbed')

    # 5. Move to Target Yellow (joint movement)
    print('\n5. Moving to Target Yellow (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block4 Targets'])
    robot.MoveL(targets['Target Yellow'])
    print('   ✅ Reached Yellow')

    # 6. Move to Target Yellow 3 (joint movement)
    print('\n5. Moving to Target Yellow 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block4 Targets'])
    robot.MoveL(targets['Target Yellow 3'])
    print('   ✅ Reached Yellow')

    # 7. Move to Target Yellow 4 (joint movement)
    print('\n5. Moving to Target Yellow 4 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block4 Targets'])
    robot.MoveL(targets['Target Yellow 4'])
    print('   ✅ Reached Yellow')

    # 8. Open gripper to release block
    print('\n6. Opening gripper to release block...')
    gripper.MoveJ(targets['Open'])
    print('   ✅ Gripper opened')

    # 9. Detach block to gripper
    print('\n7. Detaching object...')
    robot.setPoseFrame(frames['Block4'])
    tcp.DetachAll(frames['Block4'])
    print('   ✅ Block released')

    # 10. Move to Yellow 3 (joint movement)
    print('\n8. Moving to Yellow (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block4 Targets'])
    robot.MoveL(targets['Target Yellow 3'])
    print('   ✅ Reached Target Yellow 3')

    # === TRAJECTORY SEQUENCE RED ===
    print('=== Starting Trajectory Sequence ===')

    robot.setPoseFrame(frames['Block3 Targets'])

    # 1. Move to Target Red (joint movement)
    print('\n1. Moving to Target Red (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveL(targets['Target Red'])
    print('   ✅ Reached Target Red')

    # 2. Move to Red (linear movement - really slow!)
    print('\n2. Moving to Target Red 2 (linear movement - SLOW)...')
    robot.setSpeed(30)  # mm/s - really slow!
    robot.setAcceleration(20)  # mm/s²
    robot.MoveL(targets['Target Red 2'])
    print('   ✅ Reached Target Red 2')

    # 3. Close gripper to grab block
    print('\n3. Closing gripper to grab block...')
    gripper.MoveJ(targets['Close'])
    print('   ✅ Gripper closed')

    # 4. Attach block to gripper
    print('\n4. Attaching object...')
    robot.setPoseFrame(frames['Block3'])
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print('   ✅ Block grabbed')

    # 5. Move to Target Red (joint movement)
    print('\n5. Moving to Target Red (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block3 Targets'])
    robot.MoveL(targets['Target Red'])
    print('   ✅ Reached Red')

    # 6. Move to Target Red 3 (joint movement)
    print('\n5. Moving to Target Red 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block3 Targets'])
    robot.MoveL(targets['Target Red 3'])
    print('   ✅ Reached Red')

    # 7. Move to Target Red 4 (joint movement)
    print('\n5. Moving to Target Red 4 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block3 Targets'])
    robot.MoveL(targets['Target Red 4'])
    print('   ✅ Reached Red')

    # 8. Open gripper to release block
    print('\n6. Opening gripper to release block...')
    gripper.MoveJ(targets['Open'])
    print('   ✅ Gripper opened')

    # 9. Detach block to gripper
    print('\n7. Detaching object...')
    robot.setPoseFrame(frames['Block3'])
    tcp.DetachAll(frames['Block3'])
    print('   ✅ Block released')

    # 10. Move to Red 3 (joint movement)
    print('\n8. Moving to Red (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block3 Targets'])
    robot.MoveL(targets['Target Red 3'])
    print('   ✅ Reached Target Red 3')

    # === TRAJECTORY SEQUENCE GREEN FINAL ===
    print('=== Starting Trajectory Sequence ===')

    robot.setPoseFrame(frames['Block1 Targets'])

    # 1. Move to Target Green 3 (joint movement)
    print('\n1. Moving to Target Green 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveL(targets['Target Green 3'])
    print('   ✅ Reached Target Green 3')

    # 2. Move to Green (linear movement - really slow!)
    print('\n2. Moving to Target Green 4 (linear movement - SLOW)...')
    robot.setSpeed(30)  # mm/s - really slow!
    robot.setAcceleration(20)  # mm/s²
    robot.MoveL(targets['Target Green 4'])
    print('   ✅ Reached Target Green 4')

    # 3. Close gripper to grab block
    print('\n3. Closing gripper to grab block...')
    gripper.MoveJ(targets['Close'])
    print('   ✅ Gripper closed')

    # 4. Attach block to gripper
    print('\n4. Attaching object...')
    robot.setPoseFrame(frames['Block1'])
    tcp.AttachClosest(list_objects=list(blocks.values()))
    print('   ✅ Block grabbed')

    # 5. Move to Target Green 3 (joint movement)
    print('\n5. Moving to Target Green 3 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 3'])
    print('   ✅ Reached Green')

    # 6. Move to Target Green 5 (joint movement)
    print('\n5. Moving to Target Green 5 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 5'])
    print('   ✅ Reached Green')

    # 7. Move to Target Green 6 (joint movement)
    print('\n5. Moving to Target Green 6 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 6'])
    print('   ✅ Reached Green')

    # 8. Open gripper to release block
    print('\n6. Opening gripper to release block...')
    gripper.MoveJ(targets['Open'])
    print('   ✅ Gripper opened')

    # 9. Detach block to gripper
    print('\n7. Detaching object...')
    robot.setPoseFrame(frames['Block1'])
    tcp.DetachAll(frames['Block1'])
    print('   ✅ Block released')

    # 10. Move to Green (joint movement)
    print('\n8. Moving to Green 5 (joint movement)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.setPoseFrame(frames['Block1 Targets'])
    robot.MoveL(targets['Target Green 5'])
    print('   ✅ Reached Target Green 5')

    # === TRAJECTORY SEQUENCE HOME ===
    # Move robot to home
    print('Moving to Home position (from wherever the robot is)...')
    robot.setSpeedJoints(30)  # degrees/s
    robot.setAccelerationJoints(20)  # degrees/s²
    robot.MoveJ(targets['Home'])
    print('✅ Robot initialized at Home\n')

    print('\n=== Trajectory Complete ===')
    sleep(3)
    reset_blocks(blocks, frames, blockPoses)
