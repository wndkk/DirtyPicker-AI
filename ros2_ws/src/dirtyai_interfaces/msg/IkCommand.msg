# capstone_interfaces/msg/IkCommand.msg

geometry_msgs/Point target_pose  # x, y, z 타겟 좌표
float32 gripper_val              # 그리퍼 제어 값 (예: 0.0=닫힘, -1.4=열림)
int32 move_time
int32 pose_cmd                   # 0: 타겟 좌표로 IK 이동, 1: Home 자세로 이동 등