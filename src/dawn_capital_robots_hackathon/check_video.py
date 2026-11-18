import cv2

from .extract_frames import FRAME_STEP, MIN_FRAMES

# 23.97 allowed so NTSC "24 fps" (23.976) footage passes
MIN_FPS = 23.97
# above this (slow-motion modes) the sampled frame count grows with no QA benefit
MAX_FPS = 60
# bounds the number of frames sent to the model, and with it request size and cost
MAX_DURATION_S = 30
# shorter side, so portrait videos are judged the same as landscape
MIN_SHORT_SIDE = 720
# 4K; larger frames only slow decoding and bloat the saved JPEGs
MAX_SHORT_SIDE = 2160


def check_video(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    short_side = min(width, height)
    duration = frame_count / fps if fps > 0 else 0
    return [
        {"test": "min_fps_24", "passed": fps >= MIN_FPS, "value": round(fps, 2)},
        {"test": "max_fps_60", "passed": fps <= MAX_FPS, "value": round(fps, 2)},
        {"test": "min_resolution_720p", "passed": short_side >= MIN_SHORT_SIDE, "value": f"{width}x{height}"},
        {"test": "max_resolution_2160p", "passed": short_side <= MAX_SHORT_SIDE, "value": f"{width}x{height}"},
        {"test": "max_duration_30s", "passed": duration <= MAX_DURATION_S, "value": f"{duration:.1f}s"},
        # MIN_FRAMES sampled frames need frames 0, FRAME_STEP, ... to exist
        {"test": "min_frames", "passed": frame_count >= (MIN_FRAMES - 1) * FRAME_STEP + 1, "value": int(frame_count)},
    ]
