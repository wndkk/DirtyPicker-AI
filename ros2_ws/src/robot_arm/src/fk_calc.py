#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point
from capstone_vision.msg import PickTargetWorld

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
        self.pick_sub = self.create_subscription(
            PickTargetWorld,
            '/pick_target_world',
            self.vision_callback,
            10
        )
        self.fk_publisher = self.create_publisher(Point, '/fk_position', 10)
        # TF2 버퍼와 리스너 초기화 (ROS 내부의 실제 좌표값을 듣기 위함)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 사용자 정의 파라미터 (단위: m)
        self.length1 = 0.15
        self.length2 = 0.156
        self.z_offset = 0.0815

        self.pick_x = None
        self.pick_y = None

        self.create_timer(0.1, self.position_callback)

        self.position = None

    def vision_callback(self, msg):
        
        self.pick_x = -msg.x
        self.pick_y = msg.y + 0.12  # y_offset
    def position_callback(self):
        msg = Point()
        if self.position is not None:
            msg.x = self.position[0]
            msg.y = self.position[1]
            msg.z = self.position[2]
        self.fk_publisher.publish(msg)

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
        self.position = self.fk_calculation(q0, q1, q2, q3)

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
                f"조인트 각도 (rad): q0: {q0:.3f}, q1: {q1:.3f}, q2: {q2:.3f}, q3: {q3:.3f}\n"
                f"[Math] X: {self.position[0]: .5f}, Y: {self.position[1]: .5f}, Z: {self.position[2]: .5f}\n"
                f"[Pick Target]  X: {self.pick_x: .5f}, Y: {self.pick_y: .5f}\n"
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
        z = self.z_offset + self.length1 * (-math.sin(theta1) - math.sin(theta2)) - self.length2 * math.sin(theta3)

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