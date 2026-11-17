import cv2

from .extract_frames import EVERY_S, MIN_FRAMES


def check_video(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    duration = frame_count / fps if fps > 0 else 0
    return [
        # 29.97 allowed so NTSC "30 fps" footage passes
        {"test": "min_fps_30", "passed": fps >= 29.97, "value": round(fps, 2)},
        # shorter side, so portrait videos are judged the same as landscape
        {"test": "min_resolution_720p", "passed": min(width, height) >= 720, "value": f"{width}x{height}"},
        # strictly longer, as the frame at t == duration is never sampled
        {"test": "min_duration", "passed": duration > (MIN_FRAMES - 1) * EVERY_S, "value": f"{duration:.1f}s"},
    ]
