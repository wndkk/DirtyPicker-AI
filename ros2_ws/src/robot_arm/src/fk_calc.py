#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState

# TF2 관련 라이브러리 추가
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class FKTFCompare(Node):
    def __init__(self):
        super().__init__('fk_tf_compare_node')

        self.subscription = self.create_subscription(
            JointState, 
            '/joint_states', 
            self.callback, 
            10
        )

        # TF2 버퍼와 리스너 초기화 (ROS 내부의 실제 좌표값을 듣기 위함)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 사용자 정의 파라미터 (단위: m)
        self.length1 = 0.15
        self.length2 = 0.156
        self.z_offset = 0.0815

    def callback(self, msg):
        # 1. 조인트 인덱스 찾기
        try:
            idx_q0 = msg.name.index('joint0')
            idx_q1 = msg.name.index('joint1')
            idx_q2 = msg.name.index('joint2')
            idx_q3 = msg.name.index('joint3')
        except ValueError:
            return

        q0 = msg.position[idx_q0]
        q1 = msg.position[idx_q1]
        q2 = msg.position[idx_q2]
        q3 = msg.position[idx_q3]

        # 2. 내 수식으로 계산한 FK (Math FK)
        my_x, my_y, my_z = self.fk_calculation(q0, q1, q2, q3)

        # 3. ROS가 계산한 실제 좌표 (TF2) 가져오기
        try:
            # base_link를 기준으로 end_effector의 현재 위치를 물어봅니다.
            t = self.tf_buffer.lookup_transform(
                'base_link', 
                'end_effector', 
                rclpy.time.Time()
            )
            
            tf_x = t.transform.translation.x
            tf_y = t.transform.translation.y
            tf_z = t.transform.translation.z

            # 4. 결과 나란히 출력하여 비교
            self.get_logger().info(
                f"조인트 각도 (rad): q0: {q0:.4f}, q1: {q1:.4f}, q2: {q2:.4f}, q3: {q3:.4f}\n"
                f"\n[Math] X: {my_x: .4f}, Y: {my_y: .4f}, Z: {my_z: .4f}\n"
                f"[TF2]  X: {tf_x: .4f}, Y: {tf_y: .4f}, Z: {tf_z: .4f}\n"
                f"------------------------------------------------"
            )

        except TransformException as ex:
            self.get_logger().debug(f'TF를 아직 받아오지 못했습니다: {ex}')

    def fk_calculation(self, q0, q1, q2, q3):
        theta0 = q0
        theta1 = q1
        theta2 = q1 + q2
        theta3 = q1 + q2 + q3
        
        y = (self.length1 * (math.cos(theta1) + math.cos(theta2)) + self.length2 * math.cos(theta3)) * math.cos(theta0)
        x = (self.length1 * (math.cos(theta1) + math.cos(theta2)) + self.length2 * math.cos(theta3)) * math.sin(theta0)
        z = self.z_offset - self.length1 * (math.sin(theta1) + math.sin(theta2)) - self.length2 * math.sin(theta3)

        return (x, y, z)

def main(args=None):
    rclpy.init(args=args)
    node = FKTFCompare()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()