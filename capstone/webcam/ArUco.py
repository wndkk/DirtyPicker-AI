import cv2
import numpy as np
import time
import pickle
import os

# ===================== 사용자 설정 =====================
CALIB_FILE = "/home/a/Documents/capstone/webcam2_calibration_1280x720_25mm.pkl"
CAM_INDEX = 2
CAP_W, CAP_H = 1280, 720

# ArUco 마커 한 변 실측(mm)
MARKER_SIZE_MM = 80
# ======================================================


def rvec_to_euler_degrees(rvec):
    R, _ = cv2.Rodrigues(rvec)
    euler = cv2.RQDecomp3x3(R)[0]
    return np.array(euler, dtype=float)


def live_aruco_detection(calibration_data):
    camera_matrix = calibration_data["camera_matrix"]
    dist_coeffs = calibration_data["dist_coeffs"]

    # ArUco 설정 (OpenCV 4.5.x 방식)
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    aruco_params = cv2.aruco.DetectorParameters_create()

    marker_size_m = MARKER_SIZE_MM / 1000.0

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)

    if not cap.isOpened():
        raise RuntimeError(f"카메라 열기 실패: VideoCapture({CAM_INDEX})")

    time.sleep(0.5)
    dist_zeros = np.zeros((1, 5), dtype=np.float64)

    print("ArUco 검출 시작 (q로 종료)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 왜곡 보정
        undist = cv2.undistort(frame, camera_matrix, dist_coeffs)

        # 마커 검출 (OpenCV 4.5.x 방식)
        corners, ids, rejected = cv2.aruco.detectMarkers(
            undist, aruco_dict, parameters=aruco_params
        )

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(undist, corners, ids)

            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_size_m, camera_matrix, dist_zeros
            )

            for i in range(len(ids)):
                rvec = rvecs[i]
                tvec = tvecs[i]

                cv2.drawFrameAxes(
                    undist, camera_matrix, dist_zeros,
                    rvec, tvec, marker_size_m / 2
                )

                x, y, z = tvec[0]
                euler = rvec_to_euler_degrees(rvec)

                pts = corners[i][0]
                cx = int(np.mean(pts[:, 0]))
                cy = int(np.mean(pts[:, 1]))

                cv2.putText(undist, f"ID: {int(ids[i][0])}",
                            (cx, cy - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                cv2.putText(undist,
                            f"tvec(m): x={x:.3f}, y={y:.3f}, z={z:.3f}",
                            (cx, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                cv2.putText(undist,
                            f"euler(deg): {euler[0]:.1f}, {euler[1]:.1f}, {euler[2]:.1f}",
                            (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

        cv2.imshow("ArUco Detection", undist)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    if not os.path.exists(CALIB_FILE):
        print("❌ 캘리브레이션 파일 없음")
        return

    with open(CALIB_FILE, "rb") as f:
        calibration_data = pickle.load(f)

    print("✅ Calibration data loaded")
    live_aruco_detection(calibration_data)


if __name__ == "__main__":
    main()
