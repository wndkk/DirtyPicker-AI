#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from dirtyai_interfaces.msg import IkCommand
from geometry_msgs.msg import Point
from std_msgs.msg import Bool

import math


class IkCalc(Node):
    def __init__(self):
        super().__init__('ik_calc_node')
        self.get_logger().info("IK 계산 노드가 시작되었습니다.")

        # =========================
        # Publishers / Subscribers
        # =========================
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        self.calc_complete_pub = self.create_publisher(
            Bool,
            '/calc_done',
            10
        )

        self.task_planner_sub = self.create_subscription(
            IkCommand,
            '/ik_control',
            self.ik_control_callback,
            10
        )

        self.fk_position_sub = self.create_subscription(
            Point,
            '/fk_position',
            self.fk_position_callback,
            10
        )

        # =========================
        # Robot link lengths
        # =========================
        self.L1 = 0.15
        self.L2 = 0.15
        self.L3 = 0.156

        self.z_offset = 0.0815

        # =========================
        # Command values
        # =========================
        self.gripper_val = 0.2
        self.move_time = 1
        self.pose_cmd = 1

        self.saves_poses = {
            'home': [0.0, -2.1012, 1.5708, 1.5708, 0.2]
        }

        self.target_x = None
        self.target_y = None
        self.target_z = None

        self.present_x = 0.0
        self.present_y = 0.0

        self.ik_result = None

        # =========================
        # Tracking / servo settings
        # =========================
        # IK 계산 루프 주기
        self.ik_loop_period = 0.70

        # trajectory publish 주기
        # 0.40초마다 새 trajectory 전송
        self.traj_publish_period = 0.40
        self.last_traj_pub_time = None

        # tracking 중 목표점까지 이동 시간
        # 너무 작으면 급발진/덜컥거림 발생
        self.servo_move_time = 0.80

        # 목표 좌표가 5mm 이상 바뀔 때만 새 trajectory 전송
        self.last_published_target = None
        self.min_target_delta = 0.005

        self.timer = self.create_timer(
            self.ik_loop_period,
            self.tracking_loop
        )

    # ======================================================
    # Callbacks
    # ======================================================
    def ik_control_callback(self, msg):
        self.target_x = msg.target_pose.x
        self.target_y = msg.target_pose.y
        self.target_z = msg.target_pose.z

        self.gripper_val = msg.gripper_val
        self.move_time = msg.move_time
        self.pose_cmd = msg.pose_cmd

    def fk_position_callback(self, msg):
        self.present_x = msg.x
        self.present_y = msg.y

    # ======================================================
    # Main tracking loop
    # ======================================================
    def tracking_loop(self):
        if self.target_x is None or self.target_y is None or self.target_z is None:
            return

        now = self.get_clock().now()

        if self.last_traj_pub_time is not None:
            dt = (now - self.last_traj_pub_time).nanoseconds / 1e9
            if dt < self.traj_publish_period:
                return

        # --------------------------------------------------
        # Home command
        # --------------------------------------------------
        if self.pose_cmd > 0:
            if self.pose_cmd == 1:
                self.calc_complete_pub.publish(Bool(data=True))

                self.publish_trajectory(
                    self.saves_poses['home'],
                    self.move_time
                )

                self.last_traj_pub_time = now
                self.last_published_target = None

            return

        # --------------------------------------------------
        # IK tracking command
        # --------------------------------------------------
        current_target = (
            self.target_x,
            self.target_y,
            self.target_z,
            self.gripper_val
        )

        if not self.target_changed_enough(current_target):
            return

        self.ik_result = self.auto_pitch_calc(
            self.target_x,
            self.target_y,
            self.target_z,
            gripper_opening=self.gripper_val
        )

        if self.ik_result is not None:
            self.calc_complete_pub.publish(Bool(data=True))

            self.publish_trajectory(
                self.ik_result,
                self.servo_move_time
            )

            self.last_traj_pub_time = now
            self.last_published_target = current_target

        else:
            self.calc_complete_pub.publish(Bool(data=False))

    def target_changed_enough(self, current_target):
        if self.last_published_target is None:
            return True

        dx = abs(current_target[0] - self.last_published_target[0])
        dy = abs(current_target[1] - self.last_published_target[1])
        dz = abs(current_target[2] - self.last_published_target[2])
        dg = abs(current_target[3] - self.last_published_target[3])

        return (
            dx > self.min_target_delta
            or dy > self.min_target_delta
            or dz > self.min_target_delta
            or dg > 0.01
        )

    # ======================================================
    # IK calculation
    # ======================================================
    def check_joint_limits(self, joint_angles):
        joint_limits = {
            'joint0': (-1.5708, 1.5708),
            'joint1': (-2.1012, 0),
            'joint2': (-1.5708, 1.5708),
            'joint3': (-1.5708, 1.5708)
        }

        for i, joint_name in enumerate(['joint0', 'joint1', 'joint2', 'joint3']):
            if not (
                joint_limits[joint_name][0]
                <= joint_angles[i]
                <= joint_limits[joint_name][1]
            ):
                return False

        return True

    def ik_calculation(self, x, y, z, pitch_deg):
        pitch_rad = math.radians(pitch_deg)

        theta0 = math.atan2(x, y)

        r = math.sqrt(x ** 2 + y ** 2)
        z_prime = z - self.z_offset

        rw = r - self.L3 * math.cos(pitch_rad)
        zw = z_prime + self.L3 * math.sin(pitch_rad)

        d_square = rw ** 2 + zw ** 2

        cos_theta2 = (
            d_square
            - self.L1 ** 2
            - self.L2 ** 2
        ) / (2 * self.L1 * self.L2)

        if abs(cos_theta2) >= 1:
            return None

        theta2 = math.acos(cos_theta2)

        alpha = -math.atan2(zw, rw)
        beta = math.atan2(
            self.L2 * math.sin(theta2),
            self.L1 + self.L2 * cos_theta2
        )

        theta1 = alpha - beta
        theta3 = pitch_rad - theta1 - theta2

        if self.check_joint_limits([theta0, theta1, theta2, theta3]):
            return [theta0, theta1, theta2, theta3]

        return None

    def auto_pitch_calc(self, x, y, z, gripper_opening=0.0):
        valid_solutions = []

        for pitch in range(0, 91):
            result = self.ik_calculation(x, y, z, pitch)

            if result is not None:
                valid_solutions.append((pitch, result))

        if not valid_solutions:
            self.get_logger().error(
                f'유효한 IK 솔루션이 없습니다. '
                f'x={x:.3f}, y={y:.3f}, z={z:.3f}'
            )
            return None

        valid_solutions.sort(key=lambda item: abs(item[0] - 70))

        best_pitch, best_result = valid_solutions[0]
        best_result.append(gripper_opening)

        self.get_logger().info(
            f'IK OK | pitch={best_pitch}도 | '
            f'x={x:.3f}, y={y:.3f}, z={z:.3f} | '
            f'joint={best_result}'
        )

        return best_result

    # ======================================================
    # Trajectory publish
    # ======================================================
    def publish_trajectory(self, result_angles, duration_sec):
        target_joint_names = [
            'joint0',
            'joint1',
            'joint2',
            'joint3',
            'gripper_left_joint'
        ]

        traj_msg = JointTrajectory()
        traj_msg.joint_names = target_joint_names

        point = JointTrajectoryPoint()
        point.positions = result_angles

        point.time_from_start.sec = int(duration_sec)
        point.time_from_start.nanosec = int(
            (duration_sec - point.time_from_start.sec) * 1e9
        )

        traj_msg.points.append(point)
        self.traj_pub.publish(traj_msg)


def main(args=None):
    rclpy.init(args=args)
    node = IkCalc()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()