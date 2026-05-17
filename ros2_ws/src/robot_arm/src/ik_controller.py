#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from dirtyai_interfaces.msg import IkCommand
from geometry_msgs.msg import Point
from std_msgs.msg import Bool

import math
import time

class IkCalc(Node):
    def __init__(self):
        super().__init__('ik_calc_node')
        self.get_logger().info("IK 계산 노드가 시작되었습니다.")
        # 2. 로봇을 움직일 컨트롤러 토픽 퍼블리셔 생성
        self.traj_pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.calc_complete_pub = self.create_publisher(Bool, '/calc_done', 10)

        self.task_planner_sub = self.create_subscription(IkCommand, '/ik_control', self.ik_control_callback,10)
        self.fk_position_sub = self.create_subscription(Point, '/fk_position', self.fk_position_callback, 10)

        self.L1 = 0.15
        self.L2 = 0.15
        self.L3 = 0.156
        
        self.z_offset = 0.0815

        self.gripper_val = 0.2
        self.move_time = 1
        self.pose_cmd = 1

        self.saves_poses = {
            'home' : [0.0, -2.1012, 1.5708, 1.5708, 0.2]
        }

        self.target_x = None
        self.target_y = None
        self.target_z = None

        self.present_x = 0.0
        self.present_y = 0.0

        self.ik_result = None

        self.timer = self.create_timer(1, self.tracking_loop)

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

    def tracking_loop(self):

        if self.pose_cmd > 0:
            if self.pose_cmd == 1:
                self.get_logger().info("Waiting... home")
                self.calc_complete_pub.publish(Bool(data=True))
                self.publish_trajectory(self.saves_poses['home'], self.move_time)
        else:

            self.ik_result = self.auto_pitch_calc(self.target_x, self.target_y, self.target_z, gripper_opening=self.gripper_val)

            if self.ik_result is not None:
                self.calc_complete_pub.publish(Bool(data=True))
                self.publish_trajectory(self.ik_result, self.move_time)
            else:
                self.calc_complete_pub.publish(Bool(data=False))
        
    def check_joint_limits(self, joint_angles):
        joint_limits = {
            'joint0': (-1.5708, 1.5708),
            'joint1': (-2.1012, 0),
            'joint2': (-1.5708, 1.5708),
            'joint3': (-1.5708, 1.5708)
        }

        for i, joint_name in enumerate(['joint0', 'joint1', 'joint2', 'joint3']):
            if not (joint_limits[joint_name][0] <= joint_angles[i] <= joint_limits[joint_name][1]):
                # self.get_logger().error(f'{joint_name}의 각도가 범위를 벗어났습니다: {joint_angles[i]:.4f} rad')

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
            # self.get_logger().error('범위를 벗어난 위치입니다.')
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
        print(x,y,z)
        for pitch in range(0, 91):
            result = self.ik_calculation(x,y,z,pitch)

            if result is not None:
                valid_solutions.append((pitch, result))

        if not valid_solutions:
            self.get_logger().error('유효한 IK 솔루션이 없습니다.')
            return None
        
        valid_solutions.sort(key=lambda item: abs(item[0] - 60))

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