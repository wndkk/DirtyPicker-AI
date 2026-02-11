import cv2
import datetime
import os

# 저장 경로 (절대 경로)
save_dir = "/home/a/Documents/capstone/checkerboards"
os.makedirs(save_dir, exist_ok=True)

# 카메라 장치 열기
cap = cv2.VideoCapture(2)

# 해상도 고정 (중요)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

print("캘리브레이션 이미지 촬영 시작")
print(" - 'a' : 이미지 저장")
print(" - 'q' : 종료")

# 영상 캡처 루프
while True:
    ret, frame = cap.read()
    if not ret:
        print("카메라에서 프레임을 가져올 수 없습니다.")
        break

    # 프레임 표시
    cv2.imshow("Calibration Capture", frame)

    key = cv2.waitKey(1) & 0xFF

    # 'a' 키 → 이미지 저장
    if key == ord('a'):
        filename = datetime.datetime.now().strftime(
            f"{save_dir}/capture_%Y%m%d_%H%M%S.png"
        )
        cv2.imwrite(filename, frame)
        print(f"저장 완료: {filename}")

    # 'q' 키 → 종료
    elif key == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
