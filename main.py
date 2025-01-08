import cv2
import numpy as np
import matplotlib.pyplot as plt
from pupil_apriltags import Detector
from networktables import NetworkTables
import time
import requests
import json
import sys
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("--config_file", type=str, help="請提供配置檔案(json)路徑")
args = parser.parse_args()

with open(args.config_file, 'r') as file:
    content = file.read()
    configuration = json.loads(content)

fx = configuration["camera_params"]["fx"]
fy = configuration["camera_params"]["fy"]
cx = configuration["camera_params"]["cx"]
cy = configuration["camera_params"]["cy"]

# 內參矩陣
cam_mat = np.array(
    [
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1],
    ]
)
# 畸變係數
dist_coeffs = np.array(configuration["dist_coeffs"])

# AprilTag 尺寸
half_size = 6.5 / 2  # unit: inch

detector_config = configuration["aprilTag_detector"]

networkTable_server_IP = configuration["networkTable"]["server_ip"]
networkTable_table_name = configuration["networkTable"]["table_name"]
# ================================================================================

# 每個標記對應的真實三維位置和旋轉角度 
# [X(in), Y(in), Z(in), Z-Rotation(deg), Y-Rotation(deg)]
with open(configuration["aprilTag_map_path"], 'r') as file:
    content = file.read()
    tag_centers_map = json.loads(content)
tag_rotated_corners = {}

# yz旋轉矩陣
def rot_mat(z_theta, y_theta):
    z_theta = np.deg2rad(z_theta)
    y_theta = np.deg2rad(y_theta)

    Rz = np.array(
        [
            [np.cos(z_theta), -np.sin(z_theta), 0],
            [np.sin(z_theta), np.cos(z_theta), 0],
            [0, 0, 1],
        ]
    )

    Ry = np.array(
        [
            [np.cos(y_theta), 0, np.sin(y_theta)],
            [0, 1, 0],
            [-np.sin(y_theta), 0, np.cos(y_theta)],
        ]
    )

    return Rz.dot(Ry)

# corners
def get_tag_corners(tag_id):
    if tag_id not in tag_rotated_corners:
        # get center
        x, y, z, z_theta, y_theta = tag_centers_map[tag_id]
        center = np.array([x, y, z], dtype=np.float32)

        # on xz plane
        object_corners = np.array(
            [
                [0, -half_size, -half_size],  # 左下
                [0, half_size, -half_size],  # 右下
                [0, half_size, half_size],  # 右上
                [0, -half_size, half_size],  # 左上
            ],
            dtype=np.float32,
        )

        # rotate + center & store
        R = rot_mat(z_theta, y_theta)
        tag_rotated_corners[tag_id] = np.dot(object_corners, R.T) + center

    return tag_rotated_corners[tag_id]

def connection_test():
    try:
        requests.get(f'http://{networkTable_server_IP}:80', timeout=1)
        return True
    except Exception as err: 
        return False
    

if __name__ == "__main__":
    cap = cv2.VideoCapture(configuration["camera_index"])

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    attempts = 0
    conn = connection_test()
    while not conn and attempts < configuration["networkTable"]["max_attempts"]:
        conn = connection_test()
        print(f"networktable connecting(attempts: {attempts})")
        attempts += 1
        conn = False
        time.sleep(0.2)
    
    if conn:
        NetworkTables.initialize(server=networkTable_server_IP)
        table = NetworkTables.getTable(networkTable_table_name)

    detector = Detector(
        families=detector_config["families"],
        nthreads=detector_config["nthreads"],
        quad_decimate=detector_config["quad_decimate"],
        quad_sigma=detector_config["quad_sigma"],
        refine_edges=detector_config["refine_edges"],
        decode_sharpening=detector_config["decode_sharpening"],
        debug=detector_config["debug"]
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(img=gray)

        result = []
        for tag in tags:
            corners = tag.corners.reshape((4, 2))
            img_corners = corners.astype(np.float32)
            tag_id = tag.tag_id

            if tag_id in tag_centers_map:
                # solve Camera Posision
                retval, rvec, tvec = cv2.solvePnP(
                    get_tag_corners(tag_id),
                    img_corners,
                    cam_mat,
                    dist_coeffs,
                )

                if retval:
                    rot_mat, _ = cv2.Rodrigues(rvec)
                    camera_position = -rot_mat.T.dot(tvec).ravel()
                    #print("Camera Position:", camera_position)
                    result.append({
                        "tag": tag,
                        "cam_pose": {
                            "field_rot_mat": rot_mat,
                            "field_position": camera_position
                        }
                    })

        if conn:
            table.putString(configuration["networkTable"]["result_key"], json.dumps(result))
        print(result)
                    
        # break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()