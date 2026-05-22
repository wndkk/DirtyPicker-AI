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
    LIFTING_AFTER_GRASP = 6
    MOVING_TO_DROP = 7
    RELEASING = 8
    HOMING = 9


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

        # 잡는 순간 좌표 고정용
        self.grasp_x = None
        self.grasp_y = None

        self.pick_z = 0.02
        self.target_z_min = 0.02

        self.approach_height = 0.10
        self.approach_z = self.pick_z + self.approach_height
        self.target_z = self.pick_z

        # 잡은 뒤 상승 높이
        self.lift_after_grasp_z = 0.18

        self.x_offset = 0.002
        self.y_offset = 0.324

        # =========================
        # Conveyor Tracking 설정
        # =========================
        self.conveyor_speed_m_s = 0.015

        self.conveyor_axis = "x"
        self.conveyor_sign = 1.0

        self.tracking_publish_period = 0.30
        self.last_tracking_pub_time = None

        self.tracking_alpha = 0.60
        self.smooth_x = None
        self.smooth_y = None

        self.approach_lead_time = 4.8
        self.pick_lead_time = 3.5
        self.tof_lead_time = 3.5

        self.approach_track_time = 4.0
        self.target_track_time = 3.0

        self.latest_raw_x = None
        self.latest_raw_y = None
        self.latest_vision_time = None

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
        self.drop_z = 0.18

        # =========================
        # Flags
        # =========================
        self.calc_done = False
        self.ik_failed = False
        self.ik_fail_count = 0
        self.ik_fail_required = 3
        self.command_sent = False

        # =========================
        # JointState 기반 정지 판단
        # =========================
        self.joint_state_received = False
        self.prev_joint_positions = None
        self.current_joint_positions = None

        self.joint_stop_epsilon = 0.006
        self.stable_count = 0
        self.stable_required_count = 5

        # =========================
        # 그리퍼 대기 시간
        # =========================
        self.grasp_wait_time = 1.5
        self.release_wait_time = 1.3

        # =========================
        # Z 상승 대기 시간
        # =========================
        self.lift_wait_time = 1.8
        self.lift_timeout = 3.5

        # =========================
        # LOWERING_AND_TOF 대기 시간
        # =========================
        self.tof_check_wait_time = 1.5

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
    # Time helper
    # ======================================================
    def elapsed_from(self, ros_time):
        if ros_time is None:
            return 0.0

        return (self.get_clock().now() - ros_time).nanoseconds / 1e9

    # ======================================================
    # Conveyor tracking helper
    # ======================================================
    def reset_tracking(self):
        self.smooth_x = None
        self.smooth_y = None
        self.last_tracking_pub_time = None

    def update_raw_target(self, msg):
        self.latest_raw_x = -msg.x + self.x_offset
        self.latest_raw_y = -msg.y + self.y_offset
        self.latest_vision_time = self.get_clock().now()

    def predict_target(self, lead_time):
        if self.latest_raw_x is None or self.latest_raw_y is None:
            return self.target_x, self.target_y

        vision_age = self.elapsed_from(self.latest_vision_time)
        total_predict_time = max(0.0, vision_age + lead_time)

        move_m = (
            self.conveyor_sign
            * self.conveyor_speed_m_s
            * total_predict_time
        )

        pred_x = self.latest_raw_x
        pred_y = self.latest_raw_y

        if self.conveyor_axis == "x":
            pred_x += move_m
        elif self.conveyor_axis == "y":
            pred_y += move_m

        return pred_x, pred_y

    def smooth_target(self, x, y):
        if self.smooth_x is None or self.smooth_y is None:
            self.smooth_x = x
            self.smooth_y = y
        else:
            a = self.tracking_alpha
            self.smooth_x = a * x + (1.0 - a) * self.smooth_x
            self.smooth_y = a * y + (1.0 - a) * self.smooth_y

        self.target_x = self.smooth_x
        self.target_y = self.smooth_y

        return self.target_x, self.target_y

    def tracking_pub(self, z, gripper_val, pose_cmd, move_time, lead_time):
        now = self.get_clock().now()

        if self.last_tracking_pub_time is not None:
            dt = (now - self.last_tracking_pub_time).nanoseconds / 1e9
            if dt < self.tracking_publish_period:
                return

        pred_x, pred_y = self.predict_target(lead_time)
        x, y = self.smooth_target(pred_x, pred_y)

        self.target_z = z

        self.get_logger().info(
            f"[TRACK] x={x:.3f}, y={y:.3f}, z={z:.3f}, "
            f"lead={lead_time:.2f}, tof={self.tof_distance}"
        )

        self.pub_control(
            x,
            y,
            z,
            gripper_val,
            pose_cmd,
            move_time
        )

        self.last_tracking_pub_time = now
        self.reset_joint_stability()

    # ======================================================
    # State
    # ======================================================
    def change_state(self, new_state):
        # 잡는 상태로 들어가는 순간 현재 좌표 고정
        if new_state == RobotState.GRASPING:
            self.grasp_x = self.target_x
            self.grasp_y = self.target_y
            self.get_logger().info(
                f"Grasp 좌표 고정: x={self.grasp_x:.3f}, y={self.grasp_y:.3f}"
            )

        # IDLE 복귀 시 고정 좌표 초기화
        if new_state == RobotState.IDLE:
            self.grasp_x = None
            self.grasp_y = None

        self.state = new_state
        self.state_start_time = self.get_clock().now()

        self.command_sent = False
        self.ik_failed = False
        self.ik_fail_count = 0
        self.reset_joint_stability()

        if new_state in (
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
            RobotState.LOWERING_AND_TOF,
        ):
            self.reset_tracking()

        self.get_logger().info(f"[상태 전환] ---> {new_state.name}")

        if new_state in (
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
            RobotState.LIFTING_AFTER_GRASP,
            RobotState.MOVING_TO_DROP,
            RobotState.HOMING,
        ):
            self.calc_done = False

    # ======================================================
    # Callbacks
    # ======================================================
    def calc_done_callback(self, msg):
        self.calc_done = msg.data

        if msg.data:
            self.ik_fail_count = 0
            self.ik_failed = False
            return

        if self.state in (
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
            RobotState.LOWERING_AND_TOF,
            RobotState.LIFTING_AFTER_GRASP,
            RobotState.MOVING_TO_DROP,
        ):
            self.ik_fail_count += 1
            self.get_logger().warn(
                f"IK 실패 신호 수신: {self.ik_fail_count}/{self.ik_fail_required}"
            )

            if self.ik_fail_count >= self.ik_fail_required:
                self.get_logger().warn("IK 실패 연속 발생. 홈 복귀.")
                self.ik_failed = True

    def tof_callback(self, msg):
        self.tof_distance = msg.data

    def vision_callback(self, msg):
        if msg.conf < 0.3 or not msg.locked:
            return

        # 잡은 이후에는 비전 좌표 갱신하지 않음
        if self.state in (
            RobotState.GRASPING,
            RobotState.LIFTING_AFTER_GRASP,
            RobotState.MOVING_TO_DROP,
            RobotState.RELEASING,
            RobotState.HOMING,
        ):
            return

        # IDLE 또는 tracking 중에는 최신 좌표 계속 저장
        if self.state in (
            RobotState.IDLE,
            RobotState.MOVING_TO_APPROACH,
            RobotState.MOVING_TO_TARGET,
            RobotState.LOWERING_AND_TOF,
        ):
            self.update_raw_target(msg)

        # 이미 동작 중이면 새 미션 시작은 하지 않음
        if self.state != RobotState.IDLE:
            return

        self.target_x = self.latest_raw_x
        self.target_y = self.latest_raw_y

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

        if self.ik_failed:
            self.get_logger().warn("IK 실패로 인해 현재 동작 취소. 홈 복귀.")
            self.change_state(RobotState.HOMING)
            return

        # --------------------------------------------------
        # 1. 접근 위치로 이동하면서 XY tracking
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_APPROACH:
            self.approach_z = self.pick_z + self.approach_height

            self.tracking_pub(
                self.approach_z,
                0.05,
                0,
                1,
                self.approach_lead_time
            )

            if state_elapsed > self.approach_track_time:
                self.get_logger().info("접근점 tracking 완료. 집기 위치로 이동.")
                self.change_state(RobotState.MOVING_TO_TARGET)

        # --------------------------------------------------
        # 2. 집기 위치 z=0.02로 내려가면서 XY tracking
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_TARGET:
            self.tracking_pub(
                self.pick_z,
                0.05,
                0,
                1,
                self.pick_lead_time
            )

            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(
                    f"집기 위치 이동 중 물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)
                return

            if state_elapsed > self.target_track_time:
                self.get_logger().info(
                    f"집기 위치 tracking 완료. z={self.target_z:.3f}, TOF 확인."
                )
                self.change_state(RobotState.LOWERING_AND_TOF)

        # --------------------------------------------------
        # 3. TOF 확인 상태
        # --------------------------------------------------
        elif self.state == RobotState.LOWERING_AND_TOF:
            self.tracking_pub(
                self.pick_z,
                0.05,
                0,
                1,
                self.tof_lead_time
            )

            if self.tof_distance <= self.grasp_threshold:
                self.get_logger().info(
                    f"물체 감지. TOF={self.tof_distance}"
                )
                self.change_state(RobotState.GRASPING)
                return

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
            if self.grasp_x is None or self.grasp_y is None:
                self.grasp_x = self.target_x
                self.grasp_y = self.target_y

            self.pub_once(
                self.grasp_x,
                self.grasp_y,
                self.pick_z,
                1.4,
                0,
                1
            )

            if state_elapsed > self.grasp_wait_time:
                self.get_logger().info("그리퍼 닫기 완료. 잡은 좌표에서 Z축 상승.")
                self.change_state(RobotState.LIFTING_AFTER_GRASP)

        # --------------------------------------------------
        # 5. 잡은 뒤 같은 XY에서 z=0.18로 상승
        # --------------------------------------------------
        elif self.state == RobotState.LIFTING_AFTER_GRASP:
            if self.grasp_x is None or self.grasp_y is None:
                self.grasp_x = self.target_x
                self.grasp_y = self.target_y

            self.pub_once(
                self.grasp_x,
                self.grasp_y,
                self.lift_after_grasp_z,
                1.4,
                0,
                1.3
            )

            # 최소 상승 시간 확보
            if state_elapsed < self.lift_wait_time:
                return

            if self.move_finished():
                self.get_logger().info("Z축 상승 완료. 드롭 위치로 이동.")
                self.change_state(RobotState.MOVING_TO_DROP)
                return

            if state_elapsed > self.lift_timeout:
                self.get_logger().warn("Z축 상승 완료 신호 timeout. 드롭 위치로 이동.")
                self.change_state(RobotState.MOVING_TO_DROP)
                return

        # --------------------------------------------------
        # 6. 드롭 위치로 이동
        # z=0.18 높이 유지
        # --------------------------------------------------
        elif self.state == RobotState.MOVING_TO_DROP:
            self.pub_once(
                self.drop_x,
                self.drop_y,
                self.drop_z,
                1.4,
                0,
                2
            )

            if self.move_finished():
                self.get_logger().info("드롭 위치 도달. 그리퍼 열기.")
                self.change_state(RobotState.RELEASING)

        # --------------------------------------------------
        # 7. 그리퍼 열기
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
        # 8. 홈 복귀
        # --------------------------------------------------
        elif self.state == RobotState.HOMING:
            self.pub_once(
                self.target_x,
                self.target_y,
                self.target_z,
                0.05,
                1,
                1.5
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