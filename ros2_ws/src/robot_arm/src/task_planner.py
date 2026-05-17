#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from enum import Enum

# 메시지 타입 임포트 (환경에 맞게 수정 필요)
from dirtyai_interfaces.msg import PickTargetWorld, IkCommand
from std_msgs.msg import Int32, Bool

class RobotState(Enum):
    IDLE = 1               # 1. 좌표 입력 대기
    MOVING_TO_TARGET = 2   # 2. 로봇팔 타겟 위로 이동
    LOWERING_AND_TOF = 3   # 3. 하강하며 TOF 센서 확인
    GRASPING = 4           # 4. 물체 파지
    MOVING_TO_DROP = 5     # 5. 지정 장소로 이동
    RELEASING = 6          # 6. 물체 내려놓기
    HOMING = 7             # 7. 홈(대기) 위치 복귀

class TaskPlanner(Node):
    def __init__(self):
        super().__init__('task_planner_node')
        self.get_logger().info("Task Planner가 시작되었습니다. 미션 대기 중...")

        self.state = RobotState.IDLE
        self.state_start_time = self.get_clock().now()

        # 타겟 및 제어 변수
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.08      
        self.target_z_min = 0.02    # 최대 하강 높이 (바닥 충돌 방지용)
        self.x_offset = 0.08
        self.y_offset = 0.3
        # TOF 센서 및 파지 기준
        self.tof_distance = 100   # 초기값 (단위: mm 또는 m, 아두이노 세팅에 따라 다름. 여기서는 m로 가정)
        self.grasp_threshold = 105 # 파지할 TOF 거리 (예: 4cm)

        # 버리는 위치 (Drop 좌표)
        self.drop_x = -0.21316
        self.drop_y = 0.07049
        self.drop_z = 0.1

        self.calc_done = False
        # Subscribers
        self.vision_sub = self.create_subscription(PickTargetWorld, '/pick_target_world', self.vision_callback, 10)
        self.tof_sub = self.create_subscription(Int32, '/tof_sensor_data', self.tof_callback, 10) # 우노에서 올라올 데이터
        self.calc_done_sub = self.create_subscription(Bool, '/calc_done', self.calc_done_callback,10)
        # Publishers
        self.ik_controller_pub = self.create_publisher(IkCommand, '/ik_control', 10) # ik_calc 노드로 보낼 목표 좌표
        

        # 0.1초마다 상태를 확인하고 제어하는 메인 루프
        self.timer = self.create_timer(1, self.planner_loop)

    def change_state(self, new_state):
        self.state = new_state
        self.state_start_time = self.get_clock().now()
        self.get_logger().info(f"[상태 전환] ---> {new_state.name}")

    def calc_done_callback(self, msg):
        self.calc_done = msg.data

    def vision_callback(self, msg):
        # 대기 상태일 때만 새로운 타겟을 수락하여 미션 오버랩 방지
        if self.state == RobotState.IDLE:
            if msg.conf >= 0.3 and msg.locked:
                self.target_x = -msg.x + self.x_offset
                self.target_y = -msg.y + self.y_offset
                self.get_logger().info(f"YOLO 타겟 포착! (x={self.target_x:.3f}, y={self.target_y:.3f}) 미션 시작.")
                self.change_state(RobotState.MOVING_TO_TARGET)

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
        elapsed_time = (self.get_clock().now() - self.state_start_time).nanoseconds / 1e9

        if self.state == RobotState.IDLE:
            # vision_callback에서 트리거 되기를 대기
            pass

        elif self.state == RobotState.MOVING_TO_TARGET:
            # 물체 바로 위 안전 높이(0.15m)로 이동
            self.target_z = 0.08
            self.pub_control(self.target_x,self.target_y, self.target_z, 0.05, 0, 1)
            
            # 이동 완료 대기 (조인트 상태 피드백이 없으므로 임시로 2초 시간 대기)
            if self.calc_done:
                if elapsed_time > 2.0:
                    self.get_logger().info("목표 위 도달. 하강 및 TOF 측정 시작.")
                    self.change_state(RobotState.LOWERING_AND_TOF)
            else:
                self.get_logger().info("타겟 점 계산 실패")
                self.change_state(RobotState.IDLE)

        elif self.state == RobotState.LOWERING_AND_TOF:
            # Z축을 조금씩 내리면서 TOF 거리 확인 (0.1초마다 0.5cm씩 하강)
            self.target_z -= 0.02 
            if self.target_z < self.target_z_min:
                self.target_z = self.target_z_min # 바닥 충돌 방지
            
            self.pub_control(self.target_x,self.target_y, self.target_z, 0.05, 0, 1)

            # TOF 센서 조건 만족 시
            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(f"물체 감지! (거리: {self.tof_distance:.3f}m). 파지 진행.")
                self.change_state(RobotState.GRASPING)
            
            # 너무 오래 하강했는데도 못 찾으면 미션 취소
            elif elapsed_time > 5.0:
                self.get_logger().warn("물체를 찾지 못했습니다. 미션을 취소하고 복귀합니다.")
                self.change_state(RobotState.HOMING)

        elif self.state == RobotState.GRASPING:
            # 그리퍼 닫기 (0.0)
            self.pub_control(self.target_x,self.target_y, self.target_z, 1.2, 0, 1)
            
            # 그리퍼 닫히는 시간 대기
            if elapsed_time > 2.5:
                self.change_state(RobotState.MOVING_TO_DROP)

        elif self.state == RobotState.MOVING_TO_DROP:
            # 버리는 위치로 이동
            self.pub_control(self.drop_x,self.drop_y, self.drop_z, 1.2, 0, 1)
            # 이동 대기
            if elapsed_time > 2.5:
                self.change_state(RobotState.RELEASING)

        elif self.state == RobotState.RELEASING:
            # 그리퍼 열기 (-1.4)
  
            self.pub_control(self.drop_x,self.drop_y, self.drop_z, 0.05, 0, 1)
            # 열리는 시간 대기
            if elapsed_time > 2.5:
                self.change_state(RobotState.HOMING)

        elif self.state == RobotState.HOMING:
            # 초기 홈 위치로 복귀
            self.pub_control(self.target_x,self.target_y, self.target_z, 0.05, 1, 1)
            
            if elapsed_time > 2.0:
                self.get_logger().info("미션 완료! 다음 물체를 대기합니다.")
                self.change_state(RobotState.IDLE)

def main(args=None):
    rclpy.init(args=args)
    node = TaskPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()