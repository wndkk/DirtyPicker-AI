import cv2
import numpy as np
import pickle
import os

# ===================== 사용자 설정 =====================
CALIB_FILE = "/home/a/Documents/capstone/webcam2_calibration_1280x720_25mm.pkl"
CAM_INDEX = 0
CAP_W, CAP_H = 1280, 720

# 마커 중심 간 거리(mm) (TL<->TR, TL<->BL)
W_MM = 343.0
H_MM = 183.0

MARKER_SIZE_MM = 80.0
HALF = MARKER_SIZE_MM / 2.0

# 마커 ID 배치: TL, TR, BR, BL
ID_TL, ID_TR, ID_BR, ID_BL = 0, 1, 2, 3

# 저장 경로
SAVE_H_PATH = os.path.expanduser("~/Documents/capstone/calib/homography_aruco.npy")

# H 안정화(연속 OK 프레임 수)
H_OK_NEED = 10

# ======================================================

clicked_uv = None


def on_mouse(event, x, y, flags, param):
    global clicked_uv
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_uv = (x, y)


def marker_center(corners4):
    """corners4: (4,2)"""
    return corners4.mean(axis=0)


def world_corners_from_center(Xc, Yc):
    """
    월드에서 마커 중심 (Xc,Yc) 기준 코너 4개 (TL,TR,BR,BL)
    """
    return np.array([
        [Xc - HALF, Yc - HALF],  # TL
        [Xc + HALF, Yc - HALF],  # TR
        [Xc + HALF, Yc + HALF],  # BR
        [Xc - HALF, Yc + HALF],  # BL
    ], dtype=np.float32)


def detect_markers(img, aruco_dict, aruco_params):
    """
    OpenCV 버전별 ArUco detect API 차이를 흡수.
    반환: corners, ids, rejected
    """
    # 신버전(OpenCV 4.7+ 계열): ArucoDetector 클래스
    if hasattr(cv2.aruco, "ArucoDetector"):
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        return detector.detectMarkers(img)

    # 구버전: detectMarkers 함수
    return cv2.aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)


def main():
    os.makedirs(os.path.dirname(SAVE_H_PATH), exist_ok=True)

    # 1) 카메라 캘리브 로드 (undistort용)
    with open(CALIB_FILE, "rb") as f:
        calib = pickle.load(f)
    K = calib["camera_matrix"]
    dist = calib["dist_coeffs"]

    # 2) ArUco 설정 (버전 호환)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    if hasattr(cv2.aruco, "DetectorParameters"):
        aruco_params = cv2.aruco.DetectorParameters()
    else:
        # 아주 구버전 대비
        aruco_params = cv2.aruco.DetectorParameters_create()

    # 3) 카메라 열기
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)
    if not cap.isOpened():
        raise RuntimeError("카메라 열기 실패")

    win = "Aruco -> Homography (save H) | click test | s=save | q=quit"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    # 4) 월드에서 '마커 중심' 좌표(mm) 정의
    #    (원점을 보드 좌상단 느낌으로 양수화하려고 HALF를 더함)
    world_centers = {
        ID_TL: (HALF,       HALF),
        ID_TR: (HALF + W_MM, HALF),
        ID_BR: (HALF + W_MM, HALF + H_MM),
        ID_BL: (HALF,       HALF + H_MM),
    }

    need = [ID_TL, ID_TR, ID_BR, ID_BL]

    H_ok_count = 0
    H_live = None
    H_fixed = None

    print("=== ArUco Homography Save (Robust) ===")
    print(" - Put 4 markers (0,1,2,3) in view.")
    print(f" - When stable, H will be saved to: {SAVE_H_PATH}")
    print(" - Tip: all markers should face SAME direction (do NOT rotate one marker).")
    print(" - Click anywhere to see XY(mm) using current H.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("카메라 프레임 읽기 실패")
            break

        # (A) 왜곡 제거
        undist = cv2.undistort(frame, K, dist)

        # (B) 마커 검출 (버전 호환)
        corners, ids, rejected = detect_markers(undist, aruco_dict, aruco_params)

        # 상태 표시
        status_color = (0, 0, 200)

        if ids is not None and len(ids) > 0:
            # drawDetectedMarkers는 대부분 버전에서 유지됨
            cv2.aruco.drawDetectedMarkers(undist, corners, ids)
            ids_list = ids.flatten().tolist()

            if all(mid in ids_list for mid in need):
                img_pts, wld_pts = [], []

                for mid in need:
                    idx = ids_list.index(mid)

                    # (1) 이미지 코너 4개: (4,2)
                    img4 = corners[idx][0].astype(np.float32)

                    # (2) 월드 코너 4개: 중심에서 ±HALF
                    Xc, Yc = world_centers[mid]
                    wld4 = world_corners_from_center(Xc, Yc)

                    img_pts.append(img4)
                    wld_pts.append(wld4)

                    # 중심점 시각화
                    cxy = marker_center(img4)
                    cv2.circle(undist, (int(cxy[0]), int(cxy[1])), 4, (0, 255, 0), -1)

                img_pts = np.vstack(img_pts)  # (16,2)
                wld_pts = np.vstack(wld_pts)  # (16,2)

                # (C) Homography 계산 (픽셀->월드)
                H_new, inliers = cv2.findHomography(
                    img_pts, wld_pts,
                    method=cv2.RANSAC,
                    ransacReprojThreshold=3.0
                )

                if H_new is not None:
                    H_live = H_new
                    H_ok_count += 1
                    status_color = (0, 150, 0)

                    cv2.putText(
                        undist, f"H: OK ({H_ok_count}/{H_OK_NEED})",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
                    )

                    # 연속 OK면 자동 고정+저장
                    if H_fixed is None and H_ok_count >= H_OK_NEED:
                        H_fixed = H_live
                        np.save(SAVE_H_PATH, H_fixed)
                        print(f"[SAVED] H_fixed -> {SAVE_H_PATH}")
                else:
                    H_live = None
                    H_ok_count = 0
                    cv2.putText(
                        undist, "H: FAIL",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
                    )
            else:
                H_live = None
                H_ok_count = 0
                cv2.putText(
                    undist, "Need 4 markers (0,1,2,3)",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2
                )
        else:
            H_live = None
            H_ok_count = 0
            cv2.putText(
                undist, "No markers",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
            )

        # (D) 클릭 테스트: 현재 H로 클릭점 -> 월드좌표 변환
        if clicked_uv is not None:
            u, v = clicked_uv
            cv2.circle(undist, (u, v), 6, (255, 0, 0), -1)

            H_use = H_fixed if H_fixed is not None else H_live
            if H_use is not None:
                pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
                xy = cv2.perspectiveTransform(pt, H_use)[0, 0]
                X, Y = float(xy[0]), float(xy[1])

                cv2.putText(
                    undist, f"CLICK UV=({u},{v}) -> XY=({X:.1f},{Y:.1f}) mm",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                )
            else:
                cv2.putText(
                    undist, "Click ok, but H not ready",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 200), 2
                )

        # (E) 안내 문구
        cv2.putText(
            undist, "Keys: s=save(H_live)  q=quit  | Click to test XY(mm)",
            (20, CAP_H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )

        cv2.imshow(win, undist)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        # 수동 저장
        if key == ord("s") and H_live is not None:
            H_fixed = H_live
            np.save(SAVE_H_PATH, H_fixed)
            print(f"[SAVED] H_fixed(manual) -> {SAVE_H_PATH}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
