import logging

import cv2

log = logging.getLogger(__name__)

EVERY_S = 5
# a single frame can't show whether the camera moved, so fewer is an error
MIN_FRAMES = 2


def extract_frames(path, out_dir, every_s=EVERY_S):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        # some containers (webm, some mkv) don't report a frame count
        if fps <= 0 or frame_count <= 0:
            raise ValueError(f"Cannot determine duration of {path} (fps={fps}, frames={frame_count})")
        duration = frame_count / fps

        out_dir.mkdir(parents=True, exist_ok=True)
        frames = []
        for t in range(0, int(duration) + 1, every_s):
            if t >= duration:
                break
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if not ok:
                log.warning("Could not read frame at t=%ss of %s, stopping early", t, path)
                break
            frame_path = out_dir / f"frame_{t:04d}s.jpg"
            if not cv2.imwrite(str(frame_path), frame):
                raise ValueError(f"Could not write frame to {frame_path}")
            frames.append(frame_path)
    finally:
        cap.release()

    if len(frames) < MIN_FRAMES:
        raise ValueError(f"Extracted {len(frames)} frame(s) from {path}, need at least {MIN_FRAMES}")
    return frames
