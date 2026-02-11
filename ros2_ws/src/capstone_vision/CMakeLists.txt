cmake_minimum_required(VERSION 3.8)
project(capstone_vision)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/PickTargetWorld.msg"
  DEPENDENCIES builtin_interfaces
)
install(
  PROGRAMS
    vision_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

