import cv2

# nominal 30 fps; 29 because "30 fps" phone footage reports 29.3-30.1 on average (variable frame rate, NTSC)
MIN_FPS = 29.0
# above this (slow-motion modes) the sampled frame count grows with no QA benefit;
# 60.1 so nominal 60 fps passes, as reported rates drift slightly (e.g. 60.0008)
MAX_FPS = 60.1
# shortest clip in the sample data with a complete approach, insertion and settle is 4.6 s;
# the next one down (2.9 s) has no plug action at all
MIN_DURATION_S = 4
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
        {"test": "min_fps_30", "passed": fps >= MIN_FPS, "value": round(fps, 2)},
        {"test": "max_fps_60", "passed": fps <= MAX_FPS, "value": round(fps, 2)},
        {"test": "min_resolution_720p", "passed": short_side >= MIN_SHORT_SIDE, "value": f"{width}x{height}"},
        {"test": "max_resolution_2160p", "passed": short_side <= MAX_SHORT_SIDE, "value": f"{width}x{height}"},
        {"test": "min_duration_4s", "passed": duration >= MIN_DURATION_S, "value": f"{duration:.1f}s"},
        {"test": "max_duration_30s", "passed": duration <= MAX_DURATION_S, "value": f"{duration:.1f}s"},
    ]
