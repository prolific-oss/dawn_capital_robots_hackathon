import cv2

from .extract_frames import FRAME_STEP, MIN_FRAMES


def check_video(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return [
        # 29.97 allowed so NTSC "30 fps" footage passes
        {"test": "min_fps_30", "passed": fps >= 29.97, "value": round(fps, 2)},
        # shorter side, so portrait videos are judged the same as landscape
        {"test": "min_resolution_720p", "passed": min(width, height) >= 720, "value": f"{width}x{height}"},
        # MIN_FRAMES sampled frames need frames 0, FRAME_STEP, ... to exist
        {"test": "min_frames", "passed": frame_count >= (MIN_FRAMES - 1) * FRAME_STEP + 1, "value": int(frame_count)},
    ]
