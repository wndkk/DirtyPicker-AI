#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from enum import Enum

from dirtyai_interfaces.msg import PickTargetWorld, IkCommand
from std_msgs.msg import Int32, Bool
from sensor_msgs.msg import JointState


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

        # =========================
        # Target
        # =========================
        self.target_x = 0.0
        self.target_y = 0.0

        # 사용자가 유지하고 싶은 값
        self.pick_z = 0.02
        self.target_z_min = 0.02

        self.approach_height = 0.10
        self.approach_z = self.pick_z + self.approach_height
        self.target_z = self.pick_z

        self.x_offset = 0.035
        self.y_offset = 0.31

        # =========================
        # TOF
        # =========================
        self.tof_distance = 999
        self.grasp_threshold = 105

        # =========================
        # Drop
        # =========================
        self.drop_x = -0.21316
        self.drop_y = 0.07049
        self.drop_z = 0.1

        # =========================
        # Flags
        # =========================
        self.calc_done = False
        self.command_sent = False

        # =========================
        # JointState 기반 정지 판단
        # =========================
        self.joint_state_received = False
        self.prev_joint_positions = None
        self.current_joint_positions = None

        # 너무 엄격하면 MOVING_TO_TARGET에서 안 넘어감
        self.joint_stop_epsilon = 0.006
        self.stable_count = 0
        self.stable_required_count = 5

        # =========================
        # 그리퍼 대기 시간
        # =========================
        self.grasp_wait_time = 1.5
        self.release_wait_time = 1.3

        # =========================
        # LOWERING_AND_TOF 대기 시간
        # z는 0.02 그대로라서 더 내리지 않고 TOF만 확인
        # =========================
        self.tof_check_wait_time = 0.5


        
        # =========================
        # Subscribers
        # =========================
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

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        # =========================
        # Publisher
        # =========================
        self.ik_controller_pub = self.create_publisher(
            IkCommand,
            '/ik_control',
            10
        )

        self.timer = self.create_timer(0.05, self.planner_loop)

    # ======================================================
    # JointState
    # ======================================================
    def reset_joint_stability(self):
        self.stable_count = 0
        self.prev_joint_positions = self.current_joint_positions

    def joint_state_callback(self, msg):
        if len(msg.position) == 0:
            return

        self.current_joint_positions = list(msg.position)
        self.joint_state_received = True

        if self.prev_joint_positions is None:
            self.prev_joint_positions = self.current_joint_positions
            return

        if len(self.prev_joint_positions) != len(self.current_joint_positions):
            self.prev_joint_positions = self.current_joint_positions
            self.stable_count = 0
            return

        max_delta = max(
            abs(cur - prev)
            for cur, prev in zip(
                self.current_joint_positions,
                self.prev_joint_positions
            )
        )

        if max_delta < self.joint_stop_epsilon:
            self.stable_count += 1
        else:
            self.stable_count = 0

        self.prev_joint_positions = self.current_joint_positions

    def robot_stopped(self):
        return (
            self.joint_state_received
            and self.stable_count >= self.stable_required_count
        )

    def move_finished(self):
        return self.calc_done and self.robot_stopped()
       
    # ======================================================
    # State
    # ======================================================
    def change_state(self, new_state):
        self.state = new_state
        self.state_start_time = self.get_clock().now()

        self.command_sent = False
        self.reset_joint_stability()

        self.get_logger().info(f"[상태 전환] ---> {new_state.name}")

        if new_state in (
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
            RobotState.MOVING_TO_DROP,
            RobotState.HOMING,
        ):
            self.calc_done = False

    # ======================================================
    # Callbacks
    # ======================================================
    def calc_done_callback(self, msg):
        self.calc_done = msg.data

    def tof_callback(self, msg):
        self.tof_distance = msg.data

    def vision_callback(self, msg):
        if self.state != RobotState.IDLE:
            return

        if msg.conf >= 0.3 and msg.locked:
            self.target_x = -msg.x + self.x_offset
            self.target_y = -msg.y + self.y_offset

            self.target_z = self.pick_z
            self.approach_z = self.pick_z + self.approach_height

            self.get_logger().info(
                f"YOLO 타겟 포착: "
                f"x={self.target_x:.3f}, "
                f"y={self.target_y:.3f}, "
                f"approach_z={self.approach_z:.3f}, "
                f"pick_z={self.pick_z:.3f}"
            )

            self.change_state(RobotState.MOVING_TO_APPROACH)

    # ======================================================
    # Publish
    # ======================================================
    def pub_control(self, x, y, z, gripper_val, pose_cmd, move_time):
        msg = IkCommand()

        msg.target_pose.x = float(x)
        msg.target_pose.y = float(y)
        msg.target_pose.z = float(z)

        msg.gripper_val = float(gripper_val)
        msg.move_time = int(move_time)
        msg.pose_cmd = int(pose_cmd)

        self.ik_controller_pub.publish(msg)

    def pub_once(self, x, y, z, gripper_val, pose_cmd, move_time):
        if self.command_sent:
            return

        self.pub_control(
            x,
            y,
            z,
            gripper_val,
            pose_cmd,
            move_time
        )

        self.command_sent = True
        self.reset_joint_stability()

    # ======================================================
    # Main loop
    # ======================================================
    def planner_loop(self):
        state_elapsed = (
            self.get_clock().now() - self.state_start_time
        ).nanoseconds / 1e9

        if self.state == RobotState.IDLE:
            return

        # --------------------------------------------------
        # 1. 접근 위치로 이동
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_APPROACH:
            self.target_z = self.approach_z

            self.pub_once(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                0,
                1
            )

            if self.move_finished():
                self.get_logger().info("접근점 도달. 집기 위치로 이동.")
                self.change_state(RobotState.MOVING_TO_TARGET)

        # --------------------------------------------------
        # 2. 집기 위치 z=0.02로 이동
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_TARGET:
            self.target_z = self.pick_z

            self.pub_once(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                0,
                1
            )

            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(
                    f"집기 위치 이동 중 물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)
                return

            if self.move_finished():
                self.get_logger().info(
                    f"집기 위치 도달. z={self.target_z:.3f}, TOF 확인."
                )
                self.change_state(RobotState.LOWERING_AND_TOF)

        # --------------------------------------------------
        # 3. TOF 확인 상태
        # z는 0.02 그대로 유지
        # 여기서 더 내리지 않음
        # --------------------------------------------------
        elif self.state == RobotState.LOWERING_AND_TOF:
            # 같은 위치 명령 반복 publish 금지
            self.pub_once(
                self.target_x,
                self.target_y,
                self.pick_z,
                0.05,
                0,
                1
            )

            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(
                    f"물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)
                return

            # z를 더 내릴 수 없으므로 일정 시간 후 그냥 잡기 시도
            if state_elapsed > self.tof_check_wait_time:
                self.get_logger().warn(
                    f"TOF 임계값 미도달이지만 z={self.pick_z:.3f} 유지 상태라 그리퍼 닫기 시도. "
                    f"TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)

        # --------------------------------------------------
        # 4. 그리퍼 닫기
        # --------------------------------------------------
        elif self.state == RobotState.GRASPING:
            self.pub_once(
                self.target_x,
                self.target_y,
                self.pick_z,
                1.4,
                0,
                1
            )

            if state_elapsed > self.grasp_wait_time:
                self.get_logger().info("그리퍼 닫기 완료. 드롭 위치로 이동.")
                self.change_state(RobotState.MOVING_TO_DROP)

        # --------------------------------------------------
        # 5. 드롭 위치로 이동
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_DROP:
            self.pub_once(
                self.drop_x,
                self.drop_y,
                self.drop_z,
                1.4,
                0,
                1
            )

            if self.move_finished():
                self.get_logger().info("드롭 위치 도달. 그리퍼 열기.")
                self.change_state(RobotState.RELEASING)

        # --------------------------------------------------
        # 6. 그리퍼 열기
        # --------------------------------------------------
        elif self.state == RobotState.RELEASING:
            self.pub_once(
                self.drop_x,
                self.drop_y,
                self.drop_z,
                0.05,
                0,
                1
            )

            if state_elapsed > self.release_wait_time:
                self.get_logger().info("그리퍼 열기 완료. 홈으로 복귀.")
                self.change_state(RobotState.HOMING)

        # --------------------------------------------------
        # 7. 홈 복귀
        # --------------------------------------------------
        elif self.state == RobotState.HOMING:
            self.pub_once(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                1,
                1
            )

            if self.move_finished():
                self.get_logger().info("미션 완료")
                self.change_state(RobotState.IDLE)


def main(args=None):
    rclpy.init(args=args)
    node = TaskPlanner()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()