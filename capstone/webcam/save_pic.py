import cv2
import os
from datetime import datetime

# ================= 설정 =================
CAM_INDEX = 0  # 웹캠 번호 (안 되면 1, 2)
SAVE_DIR = os.path.expanduser(
    "~/Documents/capstone/model_data/model_test_images"
)
# ========================================

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    print("❌ [ERROR] 카메라 열기 실패")
    exit(1)

print("📸 웹캠 실행됨")
print("👉 S 키: 사진 저장 (여러 번 가능)")
print("👉 ESC: 종료")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ [ERROR] 프레임 읽기 실패")
        break

    cv2.imshow("Webcam Capture", frame)
    key = cv2.waitKey(1) & 0xFF

    # ESC → 종료
    if key == 27:
        print("🛑 종료")
        break

    # 'S' 키 → 저장 (여러 번 가능)
    if key == ord('s'):
        filename = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
        save_path = os.path.join(SAVE_DIR, filename)

        success = cv2.imwrite(save_path, frame)
        if success:
            print(f"✅ [SAVED] {save_path}")
        else:
            print("❌ [ERROR] 이미지 저장 실패")

cap.release()
cv2.destroyAllWindows()
