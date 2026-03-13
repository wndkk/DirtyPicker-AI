from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # 1. MoveIt 설정 패키지 지정 (수정된 부분: package_name을 move_it_robot_arm으로 변경)
    # 로봇 이름("my_robot_arm")과 MoveIt 설정 패키지("move_it_robot_arm")를 정확히 연결해야 SRDF를 찾을 수 있습니다.
    moveit_config = MoveItConfigsBuilder("my_robot_arm", package_name="move_it_robot_arm").to_moveit_configs()

    # 2. 파이썬 노드 실행 설정
    ik_python_node = Node(
        package="robot_arm", # 우리가 만든 파이썬 스크립트는 robot_arm 패키지에 있으므로 유지
        executable="move_arm.py", # CMakeLists.txt로 설치했으므로 .py 확장자까지 정확히 적어줍니다.
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
        ],
    )

    return LaunchDescription([
        ik_python_node
    ])