import cv2
import time
import numpy as np
from ultralytics import YOLO
from dataclasses import dataclass

# ================== 사용자 설정 ==================
MODEL_PATH = "/home/a/runs/detect/train/weights/best.pt"
CAM_INDEX = 0              # 네 웹캠 번호로
IMG_W, IMG_H = 1280, 720   # 캡처 해상도
CONF_THRES = 0.25          # YOLO conf 기준 (너가 쓰던 값 유지 가능)

DIRTY_CLASS_NAME = "dirty" # 학습 클래스 이름과 정확히 일치해야 함
# (만약 학습이 class id로만 쓰는 형태면 아래에서 id로 비교하도록 바꿀 수도 있음)

# 상태머신 파라미터
N_CONFIRM = 3              # CONFIRM 연속 프레임 수
M_MISS = 5                 # LOCKED에서 미검출 허용 프레임 수
COOLDOWN_SEC = 1.0         # 픽업 후 대기 시간(초)

# 락 매칭 파라미터 (둘 다 같이 사용)
MAX_CENTER_DIST = 120      # 픽셀 거리 제한 (해상도에 따라 조정)
MIN_IOU = 0.05             # IoU 최소 (너무 작으면 관계 없는 박스도 붙음)
# ================================================

# ---- 유틸 ----
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
    """
    투핑거+용기류 픽업 포인트 추천: 박스 하단 중앙에서 약간 위(y_offset_ratio)
    """
    x1, y1, x2, y2 = xyxy
    px = int((x1 + x2) / 2.0)
    py = int(y2 - (y2 - y1) * y_offset_ratio)
    return px, py

@dataclass
class Detection:
    xyxy: np.ndarray
    conf: float
    cls_id: int
    cls_name: str

class State:
    SEARCH = "SEARCH"
    CONFIRM = "CONFIRM"
    LOCKED = "LOCKED"
    COOLDOWN = "COOLDOWN"

class TargetLocker:
    def __init__(self):
        self.state = State.SEARCH

        self.candidate = None       # Detection
        self.confirm_count = 0

        self.locked = None          # Detection (마지막으로 추적된 박스)
        self.miss_count = 0

        self.cooldown_until = 0.0

    def reset_to_search(self):
        self.state = State.SEARCH
        self.candidate = None
        self.confirm_count = 0
        self.locked = None
        self.miss_count = 0

    def choose_best_dirty(self, dets):
        """
        SEARCH에서 dirty 후보를 고르는 기준.
        추천: conf 우선 + 면적 가중(너무 작은 박스 배제)
        """
        best = None
        best_score = -1
        for d in dets:
            if d.cls_name != DIRTY_CLASS_NAME:
                continue
            x1, y1, x2, y2 = d.xyxy
            area = (x2 - x1) * (y2 - y1)
            score = d.conf * 1.0 + 0.000001 * area  # 면적 가중치(매우 약하게)
            if score > best_score:
                best_score = score
                best = d
        return best

    def match_to_reference(self, dets, ref_xyxy):
        """
        LOCKED/CONFIRM에서 '이전 박스'와 가장 비슷한 박스를 찾음.
        점수 = IoU + (가까울수록 보너스)
        """
        ref_cx, ref_cy, _, _ = xyxy_to_xywh(ref_xyxy)
        best = None
        best_score = -1

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

            # dist를 점수로 바꾸기(가까울수록 큼)
            dist_score = max(0.0, 1.0 - (dist / MAX_CENTER_DIST))
            score = (1.2 * iou) + (0.8 * dist_score) + (0.2 * d.conf)
            if score > best_score:
                best_score = score
                best = d

        return best

    def update(self, dets, now):
        """
        매 프레임 호출. 상태/락 업데이트.
        return: (selected_detection, debug_message)
        """
        debug = ""

        if self.state == State.COOLDOWN:
            if now >= self.cooldown_until:
                self.reset_to_search()
                debug = "Cooldown ended -> SEARCH"
            else:
                debug = f"COOLDOWN ({self.cooldown_until - now:.2f}s left)"
                return None, debug

        if self.state == State.SEARCH:
            best = self.choose_best_dirty(dets)
            if best is None:
                debug = "SEARCH: no dirty"
                return None, debug

            # 후보를 잡고 CONFIRM으로
            self.candidate = best
            self.confirm_count = 1
            self.state = State.CONFIRM
            debug = f"SEARCH->CONFIRM (1/{N_CONFIRM})"
            return best, debug

        if self.state == State.CONFIRM:
            if self.candidate is None:
                self.reset_to_search()
                return None, "CONFIRM: candidate lost -> SEARCH"

            # 후보와 같은 객체가 있는지 찾기
            matched = self.match_to_reference(dets, self.candidate.xyxy)
            if matched is None:
                # 연속성 깨지면 다시 SEARCH
                self.reset_to_search()
                debug = "CONFIRM: continuity broken -> SEARCH"
                return None, debug

            # 연속 유지 성공
            self.candidate = matched
            self.confirm_count += 1
            debug = f"CONFIRM: {self.confirm_count}/{N_CONFIRM}"

            if self.confirm_count >= N_CONFIRM:
                self.locked = matched
                self.state = State.LOCKED
                self.miss_count = 0
                debug = "CONFIRM->LOCKED ✅"
            return matched, debug

        if self.state == State.LOCKED:
            if self.locked is None:
                self.reset_to_search()
                return None, "LOCKED: locked is None -> SEARCH"

            matched = self.match_to_reference(dets, self.locked.xyxy)
            if matched is None:
                self.miss_count += 1
                debug = f"LOCKED: miss {self.miss_count}/{M_MISS}"
                if self.miss_count > M_MISS:
                    self.reset_to_search()
                    debug += " -> SEARCH (lost)"
                    return None, debug
                # 못 찾았지만 이전 locked는 유지(로봇 안정성)
                return self.locked, debug

            # 찾았다면 locked 업데이트
            self.locked = matched
            self.miss_count = 0
            debug = "LOCKED: tracking"
            return matched, debug

        return None, "Unknown state"

    def trigger_pick_done(self, now):
        """
        로봇이 집기 완료했다고 가정할 때 호출(지금은 키 입력으로 대체).
        """
        self.state = State.COOLDOWN
        self.cooldown_until = now + COOLDOWN_SEC
        self.candidate = None
        self.confirm_count = 0
        self.locked = None
        self.miss_count = 0

def run():
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_H)

    locker = TargetLocker()

    prev_t = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed")
            break

        now = time.time()
        dt = now - prev_t
        prev_t = now
        fps = 1.0 / (dt + 1e-9)

        # YOLO 추론
        results = model.predict(frame, conf=CONF_THRES, verbose=False)

        dets = []
        r0 = results[0]
        names = r0.names  # {id: name}
        if r0.boxes is not None and len(r0.boxes) > 0:
            for b in r0.boxes:
                xyxy = b.xyxy[0].cpu().numpy().astype(float)
                conf = float(b.conf[0].cpu().numpy())
                cls_id = int(b.cls[0].cpu().numpy())
                cls_name = names.get(cls_id, str(cls_id))
                dets.append(Detection(xyxy=xyxy, conf=conf, cls_id=cls_id, cls_name=cls_name))

        # 상태머신 업데이트
        selected, debug = locker.update(dets, now)

        # ----------------- 시각화 -----------------
        # 모든 박스(참고용) 연하게 표시
        for d in dets:
            x1, y1, x2, y2 = d.xyxy.astype(int)
            color = (100, 100, 100)
            if d.cls_name == DIRTY_CLASS_NAME:
                color = (0, 180, 255)  # dirty 후보
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.putText(frame, f"{d.cls_name} {d.conf:.2f}", (x1, max(0, y1-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # 선택된(상태머신 기준) 박스 강조
        if selected is not None:
            x1, y1, x2, y2 = selected.xyxy.astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

            px, py = pick_point_from_box(selected.xyxy)
            cv2.circle(frame, (px, py), 6, (0, 0, 255), -1)
            cv2.putText(frame, f"Pick({px},{py})", (px+8, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        # HUD
        cv2.putText(frame, f"STATE: {locker.state}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
        cv2.putText(frame, f"{debug}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.putText(frame, "Keys: [P]=pick_done  [Q]=quit", (10, IMG_H-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow("YOLO Target Lock FSM", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in [ord('q'), 27]:
            break
        if key == ord('p'):
            # 로봇이 집기 완료했다고 가정(테스트용)
            locker.trigger_pick_done(now)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run()
