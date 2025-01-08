# EACP | Extendable AprilTag Camera Positioning.

> This project aims to provide a simple foundation for team creating an AprilTag locating service, which is able to send data to a roboRIO or other devices by using `pupil-apriltags`, `python-opencv`, and `pynetworktables`.

## Requirements

- Linux/Windows/macOS
- Python 3.7+
- OpenCV (`cv2`)
- NumPy (`numpy`)
- Matplotlib (`matplotlib`)
- Pupil AprilTags (`pupil-apriltags`)
- NetworkTables (`pynetworktables`)
- Requests (`requests`)

## Hardware Suggestion

- CPU: At least Qual-Core
- Memory: 4 GB or more
- OpenCV-compatible cameraa

## Installion

1. Make sure you have Python 3.7 or a higher version installed.
2. Use the following command to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```


## AprilTag Map
Please provide a JSON file containing all apriltags on field. An example is as follows：
```json
{
    "@": ["x(inch)", "y(inch)", "z(inch)", "z-rotation(deg)", "y-rotation(deg)"],
    "1": [593.68, 9.68, 53.38, 120, 0],
    "2": [637.21, 34.79, 53.38, 120, 0],
    "3": [652.73, 196.17, 57.13, 180, 0],
    "4": [652.73, 218.42, 57.13, 180, 0],
    "5": [578.77, 323.00, 53.38, 270, 0],
    "6": [72.5, 323.00, 53.38, 270, 0],
    "7": [-1.50, 218.42, 57.13, 0, 0],
    "8": [-1.50, 196.17, 57.13, 0, 0],
    "9": [14.02, 34.79, 53.38, 60, 0],
    "10": [57.54, 9.68, 53.38, 60, 0],
    "11": [468.69, 146.19, 52.00, 300, 0],
    "12": [468.69, 177.10, 52.00, 60, 0],
    "13": [441.74, 161.62, 52.00, 180, 0],
    "14": [209.48, 161.62, 52.00, 0, 0],
    "15": [182.73, 177.10, 52.00, 120, 0],
    "16": [182.73, 146.19, 52.00, 240, 0]
}
```

 ### Pre-included
|    Game  Season   | Default Unit | Tag Family | Reference |
| ----------------  | ------------ | ---------- | ---------- |
| 2024(CRESCENDO)   | inch, degree | 36h11      | [Link](https://firstfrc.blob.core.windows.net/frc2024/FieldAssets/2024LayoutMarkingDiagram.pdf) |
| 2025(REEFSCAPE)   | inch, degree | 36h11      | [Link](https://firstfrc.blob.core.windows.net/frc2025/FieldAssets/2025FieldDrawings-FieldLayoutAndMarking.pdf) |

## Configuration

> The `camera_params` and `dist_coeffs` can be obtained by executing `calibrate.py` and completing the camera calibration process.
> ```bash
> python calibrate.py
> ```

Please provide a JSON file containing the camera and system configurations. An example is as follows：
```json
{
    "camera_params": {
        "fx": 1000,
        "fy": 1000,
        "cx": 640,
        "cy": 480
    },
    "dist_coeffs": [0.1, -0.25, 0, 0, 0.32],
    "aprilTag_detector": {
        "families": "tag36h11",
        "nthreads": 4,
        "quad_decimate": 1.0,
        "quad_sigma": 0.0,
        "refine_edges": 1,
        "decode_sharpening": 0.25,
        "debug": 0
    },
    "networkTable": {
        "server_ip": "10.TE.AM.2",
        "table_name": "vision",
        "result_key": "results",
        "max_attempts": 10
    },
    "camera_index": 0,
    "aprilTag_map_path": "path/to/aprilTag_map.json"
}
```

## Usage
1.	Create and modify the `config.json` file
2.	Excute `main.py`

```bash
python main.py --config_file "path/to/config.json"
```

3.	Exit the program by pressing the `q` key

## Features
* Detect AprilTags and determine the camera position on the game field.
* Send results via NetworkTables.