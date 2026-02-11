import cv2
import numpy as np
import time
import pickle
import os

CALIB_FILE = "/home/a/Documents/capstone/webcam2_calibration_1280x720_25mm.pkl"
CAM_INDEX = 0
CAP_W, CAP_H = 1280, 720

W_MM = 343.0
H_MM = 183.0
MARKER_SIZE_MM = 80.0
HALF = MARKER_SIZE_MM / 2.0

ID_TL, ID_TR, ID_BR, ID_BL = 0, 1, 2, 3
clicked_uv = None

def on_mouse(event, x, y, flags, param):
    global clicked_uv
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_uv = (x, y)

def marker_center(c):
    pts = c.reshape(-1, 2)
    return pts.mean(axis=0)

def world_corners_from_center(Xc, Yc):
    # ArUco detectMarkers corners order: TL, TR, BR, BL
    return np.array([
        [Xc - HALF, Yc - HALF],  # TL
        [Xc + HALF, Yc - HALF],  # TR
        [Xc + HALF, Yc + HALF],  # BR
        [Xc - HALF, Yc + HALF],  # BL
    ], dtype=np.float32)

def live_xy_mm(calib):
    K = calib["camera_matrix"]
    dist = calib["dist_coeffs"]

    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    aruco_params = cv2.aruco.DetectorParameters_create()

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)
    if not cap.isOpened():
        raise RuntimeError("카메라 열기 실패")

    win = "XY(mm) 16pt Homography (click), q quit"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    # 월드에서 '마커 중심' 위치(mm) 정의 (원점은 TL 중심)
    world_centers = {
        ID_TL: (0.0,   0.0),
        ID_TR: (W_MM,  0.0),
        ID_BR: (W_MM,  H_MM),
        ID_BL: (0.0,   H_MM),
    }

    H = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        undist = cv2.undistort(frame, K, dist)

        corners, ids, _ = cv2.aruco.detectMarkers(undist, aruco_dict, parameters=aruco_params)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(undist, corners, ids)
            ids_list = ids.flatten().tolist()
            need = [ID_TL, ID_TR, ID_BR, ID_BL]

            if all(mid in ids_list for mid in need):
                img_pts = []
                wld_pts = []

                for mid in need:
                    idx = ids_list.index(mid)

                    # 이미지 코너 4개 (TL,TR,BR,BL)
                    img4 = corners[idx][0].astype(np.float32)  # (4,2)

                    # 월드 코너 4개 (해당 마커의 월드 중심에서 ±40mm)
                    Xc, Yc = world_centers[mid]
                    wld4 = world_corners_from_center(Xc, Yc)

                    img_pts.append(img4)
                    wld_pts.append(wld4)

                    # 시각화: 중심점
                    cxy = marker_center(img4)
                    cv2.circle(undist, (int(cxy[0]), int(cxy[1])), 4, (0,255,0), -1)

                img_pts = np.vstack(img_pts)  # (16,2)
                wld_pts = np.vstack(wld_pts)  # (16,2)

                H, inliers = cv2.findHomography(img_pts, wld_pts, method=cv2.RANSAC, ransacReprojThreshold=3.0)
                cv2.putText(undist, "H: OK (16 pts)", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,150,0), 2)
            else:
                H = None
                cv2.putText(undist, "Need 4 markers (0,1,2,3)", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,200), 2)
        else:
            H = None
            cv2.putText(undist, "No markers", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,200), 2)

        if clicked_uv is not None:
            u, v = clicked_uv
            cv2.circle(undist, (u, v), 6, (255,0,0), -1)

            if H is not None:
                pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
                xy = cv2.perspectiveTransform(pt, H)[0, 0]
                X, Y = float(xy[0]), float(xy[1])
                cv2.putText(undist, f"XY=({X:.1f},{Y:.1f}) mm", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            else:
                cv2.putText(undist, "Click ok, but H not ready", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,200), 2)

        cv2.imshow(win, undist)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    with open(CALIB_FILE, "rb") as f:
        calib = pickle.load(f)
    live_xy_mm(calib)

if __name__ == "__main__":
    main()
