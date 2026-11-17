import cv2


def check_video(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return [
        # 29.97 allowed so NTSC "30 fps" footage passes
        {"test": "min_fps_30", "passed": fps >= 29.97, "value": round(fps, 2)},
        # shorter side, so portrait videos are judged the same as landscape
        {"test": "min_resolution_720p", "passed": min(width, height) >= 720, "value": f"{width}x{height}"},
    ]
