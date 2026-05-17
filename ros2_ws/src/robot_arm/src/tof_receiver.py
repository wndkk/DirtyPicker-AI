#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import serial

class TofSerialNode(Node):
    def __init__(self):
        super().__init__('tof_serial_node')
        self.publisher_ = self.create_publisher(Int32, 'tof_sensor_data', 10)
        
        # 포트 이름은 환경에 따라 '/dev/ttyUSB0' 또는 '/dev/ttyACM0'일 수 있습니다.
        # 윈도우라면 'COM3' 등 형태입니다.
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
            self.get_logger().info("시리얼 포트 연결 성공!")
        except Exception as e:
            self.get_logger().error(f"연결 실패: {e}")

        # 0.05초마다 시리얼 읽기 실행
        self.timer = self.create_timer(0.05, self.read_and_publish)

    def read_and_publish(self):
        if self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line.isdigit(): # 숫자 데이터만 처리
                    msg = Int32()
                    msg.data = int(line)
                    self.publisher_.publish(msg)
                    # self.get_logger().info(f"Published: {msg.data}mm")
            except Exception as e:
                self.get_logger().warn(f"데이터 읽기 오류: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TofSerialNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()