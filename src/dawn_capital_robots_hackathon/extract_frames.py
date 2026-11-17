import logging
from pathlib import Path
from typing import NamedTuple

import cv2

log = logging.getLogger(__name__)

# keep every Nth frame
FRAME_STEP = 5
# a single frame can't show whether the camera moved, so fewer is an error
MIN_FRAMES = 2


class Frame(NamedTuple):
    path: Path
    index: int
    t: float  # seconds into the video


def extract_frames(path, out_dir, step=FRAME_STEP):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            raise ValueError(f"Cannot determine fps of {path} (fps={fps})")

        out_dir.mkdir(parents=True, exist_ok=True)
        frames = []
        index = 0
        # read sequentially: grab() skips decoding the frames we drop, and unlike
        # seeking it doesn't depend on the container reporting a frame count
        while cap.grab():
            if index % step == 0:
                ok, image = cap.retrieve()
                if ok:
                    frame_path = out_dir / f"frame_{index:06d}.jpg"
                    if not cv2.imwrite(str(frame_path), image):
                        raise ValueError(f"Could not write frame to {frame_path}")
                    frames.append(Frame(frame_path, index, index / fps))
                else:
                    log.warning("Could not decode frame %s of %s, skipping", index, path)
            index += 1
    finally:
        cap.release()

    if len(frames) < MIN_FRAMES:
        raise ValueError(f"Extracted {len(frames)} frame(s) from {path}, need at least {MIN_FRAMES}")
    return frames
