#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from enum import Enum

from dirtyai_interfaces.msg import PickTargetWorld, IkCommand
from std_msgs.msg import Int32, Bool


class RobotState(Enum):
    IDLE = 1
    MOVING_TO_APPROACH = 2
    MOVING_TO_TARGET = 3
    LOWERING_AND_TOF = 4
    GRASPING = 5
    MOVING_TO_DROP = 6
    RELEASING = 7
    HOMING = 8


class TaskPlanner(Node):
    def __init__(self):
        super().__init__('task_planner_node')
        self.get_logger().info("Task Planner 시작")

        self.state = RobotState.IDLE
        self.state_start_time = self.get_clock().now()

        self.target_x = 0.0
        self.target_y = 0.0
        self.pick_z = 0.02
        self.approach_height = 0.10
        self.approach_z = self.pick_z + self.approach_height
        self.target_z = self.pick_z
        self.target_z_min = 0.02

        self.prev_z = self.target_z

        self.x_offset = 0.035
        self.y_offset = 0.31

        # 센서값 초기값은 크게
        self.tof_distance = 999
        self.grasp_threshold = 105

        self.drop_x = -0.21316
        self.drop_y = 0.07049
        self.drop_z = 0.1

        self.calc_done = False
        self.move_timeout = 3.0

        self.vision_sub = self.create_subscription(
            PickTargetWorld,
            '/pick_target_world',
            self.vision_callback,
            10
        )

        self.tof_sub = self.create_subscription(
            Int32,
            '/tof_sensor_data',
            self.tof_callback,
            10
        )

        self.calc_done_sub = self.create_subscription(
            Bool,
            '/calc_done',
            self.calc_done_callback,
            10
        )

        self.ik_controller_pub = self.create_publisher(
            IkCommand,
            '/ik_control',
            10
        )

        # 20Hz 제어
        self.timer = self.create_timer(0.05, self.planner_loop)

    def change_state(self, new_state):
        self.state = new_state
        self.state_start_time = self.get_clock().now()
        self.get_logger().info(f"[상태 전환] ---> {new_state.name}")

        if new_state == RobotState.LOWERING_AND_TOF:
            self.prev_z = self.target_z

        if new_state in (
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
        ):
            self.calc_done = False

    def calc_done_callback(self, msg):
        self.calc_done = msg.data

    def vision_callback(self, msg):
        if self.state == RobotState.IDLE:
            if msg.conf >= 0.3 and msg.locked:
                self.target_x = -msg.x + self.x_offset
                self.target_y = -msg.y + self.y_offset
                self.target_z = self.pick_z
                self.approach_z = self.pick_z + self.approach_height

                self.get_logger().info(
                    f"YOLO 타겟 포착: x={self.target_x:.3f}, "
                    f"y={self.target_y:.3f}, 접근 z={self.approach_z:.3f}"
                )

                self.change_state(RobotState.MOVING_TO_APPROACH)

    def tof_callback(self, msg):
        self.tof_distance = msg.data

    def pub_control(self, x, y, z, gripper_val, pose_cmd, move_time):
        msg = IkCommand()
        msg.target_pose.x = float(x)
        msg.target_pose.y = float(y)
        msg.target_pose.z = float(z)
        msg.gripper_val = float(gripper_val)
        msg.move_time = int(move_time)
        msg.pose_cmd = int(pose_cmd)
        self.ik_controller_pub.publish(msg)

    def planner_loop(self):
        elapsed_time = (
            self.get_clock().now() - self.state_start_time
        ).nanoseconds / 1e9

        if self.state == RobotState.IDLE:
            return

        elif self.state == RobotState.MOVING_TO_APPROACH:
            self.target_z = self.approach_z

            self.pub_control(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                0,
                1
            )

            if self.calc_done and elapsed_time > 2.0:
                self.get_logger().info("접근점 도달. 집기 좌표로 수직 하강.")
                self.change_state(RobotState.MOVING_TO_TARGET)

            elif not self.calc_done and elapsed_time > self.move_timeout:
                self.get_logger().warn("접근점 IK 계산 실패 또는 미완료")
                self.change_state(RobotState.IDLE)

        elif self.state == RobotState.MOVING_TO_TARGET:
            self.target_z = self.pick_z

            self.pub_control(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                0,
                1.5
            )

            if self.tof_distance <= self.grasp_threshold and elapsed_time > 1.0:
                self.get_logger().info(
                    f"집기 좌표에서 물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)

            elif self.calc_done and elapsed_time > 2.0:
                self.get_logger().info("집기 좌표 도달. TOF 기반 미세 하강 시작.")
                self.change_state(RobotState.LOWERING_AND_TOF)

            elif not self.calc_done and elapsed_time > self.move_timeout:
                self.get_logger().warn("집기 좌표 IK 계산 실패 또는 미완료")
                self.change_state(RobotState.HOMING)

        elif self.state == RobotState.LOWERING_AND_TOF:
            # 초반 빠르게, 가까워질수록 천천히
            if self.tof_distance > 200:
                dz = 0.002
            elif self.tof_distance > 140:
                dz = 0.001
            else:
                dz = 0.0005

            self.target_z -= dz

            if self.target_z < self.target_z_min:
                self.target_z = self.target_z_min

            # 1mm 이상 변했을 때만 명령 전송
            if abs(self.prev_z - self.target_z) >= 0.001:
                self.pub_control(
                    self.target_x,
                    self.target_y,
                    self.target_z,
                    0.05,
                    0,
                    1
                )
                self.prev_z = self.target_z

            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(
                    f"물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)

            elif elapsed_time > 5.0:
                self.get_logger().warn("물체 감지 실패. 복귀.")
                self.change_state(RobotState.HOMING)

        elif self.state == RobotState.GRASPING:
            self.pub_control(
                self.target_x,
                self.target_y,
                self.target_z,
                1.4,
                0,
                1
            )

            if elapsed_time > 2.5:
                self.change_state(RobotState.MOVING_TO_DROP)

        elif self.state == RobotState.MOVING_TO_DROP:
            self.pub_control(
                self.drop_x,
                self.drop_y,
                self.drop_z,
                1.4,
                0,
                1
            )

            if elapsed_time > 2.5:
                self.change_state(RobotState.RELEASING)

        elif self.state == RobotState.RELEASING:
            self.pub_control(
                self.drop_x,
                self.drop_y,
                self.drop_z,
                0.05,
                0,
                1
            )

            if elapsed_time > 2.5:
                self.change_state(RobotState.HOMING)

        elif self.state == RobotState.HOMING:
            self.pub_control(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                1,
                1
            )

            if elapsed_time >0.8:
                self.get_logger().info("미션 완료")
                self.change_state(RobotState.IDLE)


def main(args=None):
    rclpy.init(args=args)
    node = TaskPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
