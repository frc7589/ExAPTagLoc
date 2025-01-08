import cv2
import numpy as np

# 設定棋盤格大小和內部格子數量
checkerboard_size = (7, 10) # (如8x11 需皆-1)
square_size = 20  # 每個格子的大小 (mm)

objp = np.zeros((np.prod(checkerboard_size), 3), np.float32)
objp[:, :2] = np.indices(checkerboard_size).T.reshape(-1, 2)
objp *= square_size

objpoints = []
imgpoints = []

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("無法讀取相機影像")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        objpoints.append(objp)

        cv2.drawChessboardCorners(frame, checkerboard_size, corners2, ret)

    sample_count = len(imgpoints)
    cv2.putText(frame, f'Samples: {sample_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

cap.release()
cv2.destroyAllWindows()

print("Camera Config:")
print({
    "camera_params": {
        "fx": mtx[0][0],
        "fy": mtx[1][1],
        "cx": mtx[0][2],
        "cy": mtx[1][2]
    },
    "dist_coeffs": dist
}, end="\n")