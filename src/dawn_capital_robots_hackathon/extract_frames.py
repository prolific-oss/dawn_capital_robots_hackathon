import cv2


def extract_frames(path, out_dir, every_s=5):
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(path))
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    frames = []
    for t in range(0, int(duration) + 1, every_s):
        if t >= duration:
            break
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        frame_path = out_dir / f"frame_{t:04d}s.jpg"
        cv2.imwrite(str(frame_path), frame)
        frames.append(frame_path)
    cap.release()
    return frames
