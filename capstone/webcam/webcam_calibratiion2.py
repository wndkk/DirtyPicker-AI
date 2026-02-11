import cv2
import numpy as np
import os
import glob
import pickle

# ===================== 사용자 설정 =====================
IMAGE_DIR = "/home/a/Documents/capstone/checkerboards"
CALIB_FILE = "/home/a/Documents/capstone/webcam2_calibration_1280x720_25mm.pkl"

# 사용할 카메라 인덱스 (중요)
CAM_INDEX = 2

# 체커보드 내부 코너 개수 (8x6 vertices)
CHECKERBOARD = (8, 6)

# 한 칸 실제 크기: 25mm = 0.025m
SQUARE_SIZE_M = 0.025

# 캡처 해상도 (캘리/실시간 동일하게 유지 권장)
CAP_W, CAP_H = 1280, 720
# ======================================================


def calibrate_camera():
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objpoints = []
    imgpoints = []

    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE_M

    pattern = os.path.join(IMAGE_DIR, "*.png")
    images = sorted(glob.glob(pattern))
    if len(images) == 0:
        raise FileNotFoundError(f"캘리브레이션 이미지가 없습니다: {pattern}")

    gray_size = None
    used = 0

    print(f"총 이미지 개수: {len(images)}")
    print("코너 검출 시작...")

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            print(f"[SKIP] 이미지 로드 실패: {fname}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_size = gray.shape[::-1]  # (w, h)

        ret, corners = cv2.findChessboardCorners(
            gray,
            CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH
            + cv2.CALIB_CB_FAST_CHECK
            + cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        if ret:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners2)
            used += 1

            vis = cv2.drawChessboardCorners(img.copy(), CHECKERBOARD, corners2, ret)
            cv2.imshow("Corners (auto next)", vis)
            cv2.waitKey(200)
        else:
            print(f"[NO CORNERS] {os.path.basename(fname)}")

    cv2.destroyAllWindows()

    if used < 10:
        raise RuntimeError(f"코너 검출 성공 이미지가 너무 적습니다: {used}장 (권장 15~25장)")

    print(f"코너 검출 성공: {used}장")
    print("캘리브레이션 계산 중...")

    rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray_size, None, None
    )

    print("\n=== Calibration Result ===")
    print("RMS reprojection error:", rms)
    print("\nCamera matrix (K):\n", mtx)
    print("\nDistortion coeffs:\n", dist)

    calibration_data = {
        "camera_index": CAM_INDEX,
        "camera_matrix": mtx,
        "dist_coeffs": dist,
        "rvecs": rvecs,
        "tvecs": tvecs,
        "checkerboard": CHECKERBOARD,
        "square_size_m": SQUARE_SIZE_M,
        "image_dir": IMAGE_DIR,
        "capture_resolution": (CAP_W, CAP_H),
        "rms_error": float(rms),
    }

    os.makedirs(os.path.dirname(CALIB_FILE), exist_ok=True)
    with open(CALIB_FILE, "wb") as f:
        pickle.dump(calibration_data, f)

    print(f"\n✅ 캘리브레이션 결과 저장 완료: {CALIB_FILE}")
    return calibration_data


def live_video_correction(calibration_data):
    mtx = calibration_data["camera_matrix"]
    dist = calibration_data["dist_coeffs"]

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)

    if not cap.isOpened():
        raise RuntimeError(f"카메라를 열 수 없습니다. VideoCapture({CAM_INDEX}) 확인 필요")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("첫 프레임을 읽지 못했습니다.")

    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    print("실시간 왜곡 보정 시작 (q로 종료)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

        x, y, rw, rh = roi
        if rw > 0 and rh > 0:
            dst = dst[y:y + rh, x:x + rw]

        original = cv2.resize(frame, (640, 480))
        corrected = cv2.resize(dst, (640, 480))
        combined = np.hstack((original, corrected))

        cv2.imshow("Original | Corrected", combined)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if os.path.exists(CALIB_FILE):
        print("Loading existing calibration data...")
        with open(CALIB_FILE, "rb") as f:
            calibration_data = pickle.load(f)
        print(f"✅ 로드 완료: {CALIB_FILE}")
    else:
        print("Performing new camera calibration...")
        calibration_data = calibrate_camera()

    print("Starting live video correction...")
    live_video_correction(calibration_data)
