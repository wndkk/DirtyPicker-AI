#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from capstone_vision.msg import PickTargetWorld

import math
import time

class IkCalc(Node):
    def __init__(self):
        super().__init__('ik_calc_node')
        self.get_logger().info("IK 계산 노드가 시작되었습니다.")
        # 2. 로봇을 움직일 컨트롤러 토픽 퍼블리셔 생성
        self.traj_pub = self.create_publisher(JointTrajectory, '/manipulator_controller/joint_trajectory', 10)
        self.vision_sub = self.create_subscription(PickTargetWorld, '/pick_target_world', self.vision_callback, 10)

        self.L1 = 0.15
        self.L2 = 0.15
        self.L3 = 0.156
        self.z_offset = 0.0815

        self.saves_poses = {
            'home' : [0.0, -2.1012, 1.5708, 1.5708, 0.0]
        }

        self.target_x = None
        self.target_y = None
        self.target_z = 0.12

        self.timer = self.create_timer(0.1, self.tracking_loop)

    def vision_callback(self, msg):

        if not msg.locked or msg.conf < 0.3:
            self.get_logger().warn("confidence is low or not locked. Ignoring target.")
            return
        
        self.target_x = msg.x
        self.target_y = msg.y

        self.get_logger().info(f"target: x={self.target_x:.3f} m, y={self.target_y:.3f} m")

    def tracking_loop(self):

        if self.target_x is not None and self.target_y is not None:
            temp_r = math.sqrt(self.target_x**2 + self.target_y**2)
            self.get_logger().info(f"target distance: {temp_r:.3f} m")
            if not temp_r < 0.45:
                self.get_logger().warn("목적지가 너무 멀리 있습니다. 무시합니다.")
                return
             
            ik_result = self.auto_pitch_calc(self.target_x, self.target_y, self.target_z, gripper_opening=-1.5)

            if ik_result is not None:

                self.publish_trajectory(ik_result, 0.5)
        
        else:
            self.get_logger().info("Not target anything. Waiting... home")
            self.publish_trajectory(self.saves_poses['home'], 0.5)

    def check_joint_limits(self, joint_angles):
        joint_limits = {
            'joint0': (-1.5708, 1.5708),
            'joint1': (-2.1012, 0),
            'joint2': (-1.5708, 1.5708),
            'joint3': (-1.5708, 1.5708)
        }

        for i, joint_name in enumerate(['joint0', 'joint1', 'joint2', 'joint3']):
            if not (joint_limits[joint_name][0] <= joint_angles[i] <= joint_limits[joint_name][1]):
                self.get_logger().error(f'{joint_name}의 각도가 범위를 벗어났습니다: {joint_angles[i]:.4f} rad')

                return False
        return True
    
    def ik_calculation(self, x, y, z, pitch_deg):
        
        pitch_rad = math.radians(pitch_deg)
        theta0 = math.atan2(x,y)

        r = math.sqrt(x**2 + y**2)
        z_prime = z - self.z_offset

        rw = r - self.L3 * math.cos(pitch_rad)
        zw = z_prime + self.L3 * math.sin(pitch_rad)

        D_square = rw**2 + zw**2
        cos_theta2 = (D_square - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)

        if abs(cos_theta2) >= 1:
            self.get_logger().error('범위를 벗어난 위치입니다.')
            return None
        
        theta2 = math.acos(cos_theta2)

        alpha = -math.atan2(zw, rw)
        beta = math.atan2(self.L2 * math.sin(theta2), self.L1 + self.L2 * cos_theta2)

        theta1 = alpha - beta
        theta3 = pitch_rad - theta1 - theta2

        if self.check_joint_limits([theta0, theta1, theta2, theta3]):
            return [theta0, theta1, theta2, theta3]
        return None

    def auto_pitch_calc(self, x, y, z, gripper_opening=0.0):
        valid_solutions = []

        for pitch in range(0, 91):
            result = self.ik_calculation(x,y,z,pitch)

            if result is not None:
                valid_solutions.append((pitch, result))

        if not valid_solutions:
            self.get_logger().error('유효한 IK 솔루션이 없습니다.')
            return None
        
        valid_solutions.sort(key=lambda item: abs(item[0] - 70))

        best_pitch, best_result = valid_solutions[0] 
        best_result.append(gripper_opening)
        self.get_logger().info(f'최적의 pitch 각도: {best_pitch}도, 관절 각도: {best_result}')
        
        return best_result
    
    def publish_trajectory(self, result_angles, duration_sec):
        
        target_joint_names = ['joint0', 'joint1', 'joint2', 'joint3', 'gripper_left_joint']

        traj_msg = JointTrajectory()
        traj_msg.joint_names = target_joint_names
        
        point = JointTrajectoryPoint()
        point.positions = result_angles
        point.time_from_start.sec = int(duration_sec)
        point.time_from_start.nanosec = int((duration_sec - point.time_from_start.sec) * 1e9)

        traj_msg.points.append(point)
        self.traj_pub.publish(traj_msg)              

def main(args=None):
    rclpy.init(args=args)
    node = IkCalc()
    rclpy.spin(node) # 응답을 받을 때까지 대기
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()