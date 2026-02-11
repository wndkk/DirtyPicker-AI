import cv2
import os
from datetime import datetime

# ================= 설정 =================
CAM_INDEX = 0
SAVE_ROOT = os.path.expanduser(
    "~/Documents/capstone/model_data/model_test_video"
)
RAW_DIR = os.path.join(SAVE_ROOT, "raw")
FPS = 20.0
# ========================================

os.makedirs(RAW_DIR, exist_ok=True)

cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    print("❌ 카메라 열기 실패")
    exit(1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

filename = datetime.now().strftime("vid_%Y%m%d_%H%M%S.mp4")
save_path = os.path.join(RAW_DIR, filename)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(save_path, fourcc, FPS, (width, height))

print("🎥 원본 영상 촬영")
print("👉 R : 녹화 시작")
print("👉 S : 녹화 종료 및 저장")
print("👉 ESC : 종료")

recording = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()
    if recording:
        out.write(frame)
        cv2.putText(display, "REC", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    cv2.imshow("Raw Video Recorder", display)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break
    elif key == ord('r'):
        if not recording:
            recording = True
            print("⏺️ 녹화 시작")
    elif key == ord('s'):
        if recording:
            recording = False
            print("✅ 저장 완료:", save_path)

cap.release()
out.release()
cv2.destroyAllWindows()
