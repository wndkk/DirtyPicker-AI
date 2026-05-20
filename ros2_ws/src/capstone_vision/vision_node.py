#!/usr/bin/env python3
import os
import cv2
import numpy as np
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from ultralytics import YOLO
from dirtyai_interfaces.msg import PickTargetWorld

# ===================== 설정 =====================
MODEL_PATH = "/home/a/DirtyPicker-AI/model/0507best.pt"
H_PATH = os.path.expanduser("/home/a/DirtyPicker-AI/capstone/calib/homography_aruco.npy")

CAM_INDEX = 0
CAP_W, CAP_H = 1280, 720

CONF_THRES = 0.25
DIRTY_CLASS_NAME = "dirty"

N_CONFIRM = 3
M_MISS = 5
MAX_CENTER_DIST = 120
MIN_IOU = 0.05

Y_OFFSET_RATIO = 0.15
PUBLISH_HZ = 30.0
PICK_START_U = 400
# 디버그 창 띄울지 (서버/헤드리스면 False)
SHOW_DEBUG = True
# ==============================================


def xyxy_to_xywh(xyxy):
    x1, y1, x2, y2 = xyxy
    w = x2 - x1
    h = y2 - y1
    cx = x1 + w / 2.0
    cy = y1 + h / 2.0
    return cx, cy, w, h


def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    iw = max(0, inter_x2 - inter_x1)
    ih = max(0, inter_y2 - inter_y1)
    inter = iw * ih
    area_a = max(0, (ax2 - ax1)) * max(0, (ay2 - ay1))
    area_b = max(0, (bx2 - bx1)) * max(0, (by2 - by1))
    union = area_a + area_b - inter + 1e-9
    return inter / union


def pick_point_from_box(xyxy, y_offset_ratio=0.15):
    x1, y1, x2, y2 = xyxy
    u = (x1 + x2) / 2.0
    v = y2 - (y2 - y1) * y_offset_ratio
    return float(u), float(v)


def uv_to_world(H, u, v):
    pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
    xy = cv2.perspectiveTransform(pt, H)[0, 0]
    return float(xy[0]), float(xy[1])


@dataclass
class Det:
    xyxy: np.ndarray
    conf: float
    cls_id: int
    cls_name: str


class State:
    SEARCH = "SEARCH"
    CONFIRM = "CONFIRM"
    LOCKED = "LOCKED"


class Locker:
    def __init__(self):
        self.state = State.SEARCH
        self.cand = None
        self.cnt = 0
        self.lock = None
        self.miss = 0

    def reset(self):
        self.state = State.SEARCH
        self.cand = None
        self.cnt = 0
        self.lock = None
        self.miss = 0

    def choose_best_dirty(self, dets):
        best, best_score = None, -1
        for d in dets:
            if d.cls_name != DIRTY_CLASS_NAME:
                continue
            x1, y1, x2, y2 = d.xyxy
            area = (x2 - x1) * (y2 - y1)
            score = d.conf + 1e-6 * area
            if score > best_score:
                best_score = score
                best = d
        return best

    def match_ref(self, dets, ref_xyxy):
        ref_cx, ref_cy, _, _ = xyxy_to_xywh(ref_xyxy)
        best, best_score = None, -1
        for d in dets:
            if d.cls_name != DIRTY_CLASS_NAME:
                continue
            cx, cy, _, _ = xyxy_to_xywh(d.xyxy)
            dist = np.hypot(cx - ref_cx, cy - ref_cy)
            if dist > MAX_CENTER_DIST:
                continue
            iou = iou_xyxy(d.xyxy, ref_xyxy)
            if iou < MIN_IOU:
                continue
            dist_score = max(0.0, 1.0 - dist / MAX_CENTER_DIST)
            score = 1.2 * iou + 0.8 * dist_score + 0.2 * d.conf
            if score > best_score:
                best_score = score
                best = d
        return best

    def update(self, dets):
        if self.state == State.SEARCH:
            best = self.choose_best_dirty(dets)
            if best is None:
                return None, "SEARCH: no dirty"
            self.cand = best
            self.cnt = 1
            self.state = State.CONFIRM
            return best, f"SEARCH->CONFIRM (1/{N_CONFIRM})"

        if self.state == State.CONFIRM:
            m = self.match_ref(dets, self.cand.xyxy) if self.cand is not None else None
            if m is None:
                self.reset()
                return None, "CONFIRM broken -> SEARCH"
            self.cand = m
            self.cnt += 1
            if self.cnt >= N_CONFIRM:
                self.lock = m
                self.state = State.LOCKED
                self.miss = 0
                return m, "CONFIRM->LOCKED ✅"
            return m, f"CONFIRM {self.cnt}/{N_CONFIRM}"

        if self.state == State.LOCKED:
            m = self.match_ref(dets, self.lock.xyxy) if self.lock is not None else None
            if m is None:
                self.miss += 1
                if self.miss > M_MISS:
                    self.reset()
                    return None, "LOCKED lost -> SEARCH"
                return self.lock, f"LOCKED miss {self.miss}/{M_MISS}"
            self.lock = m
            self.miss = 0
            return m, "LOCKED tracking"

        return None, "Unknown"


class VisionNode(Node):
    def __init__(self):
        super().__init__("vision_node")

        if not os.path.exists(H_PATH):
            raise FileNotFoundError(f"Homography not found: {H_PATH}")

        self.H = np.load(H_PATH)
        self.model = YOLO(MODEL_PATH)

        self.cap = cv2.VideoCapture(CAM_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)

        self.locker = Locker()

        self.pub = self.create_publisher(PickTargetWorld, "/pick_target_world", 10)

        self.timer = self.create_timer(1.0 / PUBLISH_HZ, self.tick)

        if SHOW_DEBUG:
            cv2.namedWindow("YOLO LOCK -> WORLD (ROS2)")

    def tick(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # YOLO inference
        results = self.model.predict(frame, conf=CONF_THRES, verbose=False)
        r0 = results[0]
        names = r0.names

        dets = []
        if r0.boxes is not None and len(r0.boxes) > 0:
            for b in r0.boxes:
                xyxy = b.xyxy[0].cpu().numpy().astype(float)
                conf = float(b.conf[0].cpu().numpy())
                cls_id = int(b.cls[0].cpu().numpy())
                cls_name = names.get(cls_id, str(cls_id))
                dets.append(Det(xyxy=xyxy, conf=conf, cls_id=cls_id, cls_name=cls_name))

        #sel, debug = self.locker.update(dets)
        ##수정x좌표 540 이상인 dirty만 lock 대상으로 사용
        pickable_dets = []

        for d in dets:
            if d.cls_name != DIRTY_CLASS_NAME:
                continue

            u_pick, v_pick = pick_point_from_box(d.xyxy, Y_OFFSET_RATIO)

            if u_pick >= PICK_START_U:
                pickable_dets.append(d)

        sel, debug = self.locker.update(pickable_dets)


        # ✅ publish rule: LOCKED일 때만 publish
        #if self.locker.state == State.LOCKED and sel is not None:
         #   u, v = pick_point_from_box(sel.xyxy, Y_OFFSET_RATIO)
          #  x_mm, y_mm = uv_to_world(self.H, u, v)


        if self.locker.state == State.LOCKED and sel is not None:
            u, v = pick_point_from_box(sel.xyxy, Y_OFFSET_RATIO)

            if u < PICK_START_U:
                self.get_logger().warn(
                    f"작업 영역 밖 lock 해제: u={u:.1f}"
                )
                self.locker.reset()

                msg = PickTargetWorld()
                msg.x = 0.0
                msg.y = 0.0
                msg.label = ""
                msg.locked = False
                msg.conf = -1.0
                msg.stamp = self.get_clock().now().to_msg()
                self.pub.publish(msg)
                return

            x_mm, y_mm = uv_to_world(self.H, u, v)


            msg = PickTargetWorld()
            msg.x = float(x_mm/1000)  # mm -> m
            msg.y = float(y_mm/1000)  # mm -> m
            msg.label = "dirty"
            msg.locked = True
            msg.conf = float(sel.conf)
            msg.stamp = self.get_clock().now().to_msg()
            self.pub.publish(msg)
        else:
            # LOCKED가 아니면 잠금 해제 메시지 publish
            msg = PickTargetWorld()
            msg.x = 0.0
            msg.y = 0.0
            msg.label = ""
            msg.locked = False
            msg.conf = -1.0
            msg.stamp = self.get_clock().now().to_msg()
            self.pub.publish(msg)
        # debug view (optional)
        if SHOW_DEBUG:
            for d in dets:
                x1, y1, x2, y2 = d.xyxy.astype(int)
                col = (0, 180, 255) if d.cls_name == DIRTY_CLASS_NAME else (120, 120, 120)
                cv2.rectangle(frame, (x1, y1), (x2, y2), col, 1)

            if sel is not None:
                x1, y1, x2, y2 = sel.xyxy.astype(int)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

                u, v = pick_point_from_box(sel.xyxy, Y_OFFSET_RATIO)
                cv2.circle(frame, (int(u), int(v)), 6, (0, 0, 255), -1)
                Xw, Yw = uv_to_world(self.H, u, v)
                cv2.putText(frame, f"World XY=({Xw:.1f},{Yw:.1f}) mm",
                            (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.putText(frame, f"STATE: {self.locker.state}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(frame, debug, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            
            
            cv2.line(
                frame,
                (PICK_START_U, 0),
                (PICK_START_U, frame.shape[0]),
                (0, 0, 255),
                2
            )
            cv2.putText(
                frame,
                "PICK AREA START",
                (PICK_START_U + 10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

            cv2.imshow("YOLO LOCK -> WORLD (ROS2)", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in [ord("q"), 27]:
                rclpy.shutdown()

    def destroy_node(self):
        try:
            if self.cap is not None:
                self.cap.release()
            if SHOW_DEBUG:
                cv2.destroyAllWindows()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = VisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

