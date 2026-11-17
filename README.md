# Dawn Capital Robots Hackathon

A video quality gate for robot demonstration footage. It checks that a video of a plug being inserted into a socket is good enough to use, for example as training data.

Each video goes through two stages:

1. **Technical checks** (OpenCV)
   - `min_fps_24` / `max_fps_60`: between 24 and 60 fps (23.976 is accepted so NTSC footage passes).
   - `min_resolution_720p` / `max_resolution_2160p`: the shorter side is between 720 and 2160 px.
   - `min_frames`: enough frames to sample at least two (6 with the default step of 5).
2. **Visual checks** (OpenAI vision model). These run only if the technical checks pass.
   - `stable_camera`: the camera doesn't shake, pan, tilt or zoom.
   - `plug_and_socket_visible`: the plug and socket are in frame, in focus, well lit and not blocked.

   Every 5th frame is sampled and sent to the model together. The model returns a pass/fail and a short reason for each check.

If the technical checks fail, the visual checks are marked as failed ("skipped") and no API call is made. A video passes overall only if every check passes.

## Layout

All code lives in the `dawn_capital_robots_hackathon` package under `src/`.

| File | Purpose |
|---|---|
| `main.py` | CLI entry point. Runs the pipeline and writes the reports. |
| `check_video.py` | FPS and resolution checks. |
| `extract_frames.py` | Saves every 5th frame as a JPEG. |
| `analyse_frames.py` | Sends frames to the vision model and parses the structured `Verdict`. |
| `prompt.py` | The prompt that defines the visual checks. |

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
```

## Usage

```sh
# Process every video in ./videos (.mp4, .mov, .avi, .mkv, .webm)
uv run check-videos

# Process a single file or another directory
uv run check-videos path/to/video.mov
uv run check-videos path/to/dir
```

The console prints one line per video: `PASS`, `FAIL` or `ERROR`.

## Output

For each video, `output/<video-name>/` contains:

- `frames/`: the sampled frames (`frame_000000.jpg`, `frame_000005.jpg`, ... named by source frame index).
- `report.json`: the overall result and each check's result.

A combined `output/report.json` covers every video in the run: a `summary` (total, passed, failed, errors) and a `videos` list holding each video's report (or an `error` message if processing crashed).

```json
{
  "video": "videos/example1.mov",
  "passed": true,
  "tests": [
    {"test": "min_fps_24", "passed": true, "value": 30.0},
    {"test": "max_fps_60", "passed": true, "value": 30.0},
    {"test": "min_resolution_720p", "passed": true, "value": "1920x1080"},
    {"test": "max_resolution_2160p", "passed": true, "value": "1920x1080"},
    {"test": "min_frames", "passed": true, "value": 360},
    {"test": "stable_camera", "passed": true, "reason": "..."},
    {"test": "plug_and_socket_visible", "passed": true, "reason": "..."}
  ]
}
```

## Customising

- **Model and reasoning effort**: set `MODEL` and `REASONING_EFFORT` in `src/dawn_capital_robots_hackathon/analyse_frames.py`.
- **Prompt or criteria**: edit `src/dawn_capital_robots_hackathon/prompt.py`. If you add a check, add a matching field to `Verdict` in `src/dawn_capital_robots_hackathon/analyse_frames.py`.
- **Sampling rate**: change `FRAME_STEP` (keep every Nth frame) in `src/dawn_capital_robots_hackathon/extract_frames.py`.
- **Thresholds**: change the FPS and resolution limits in `src/dawn_capital_robots_hackathon/check_video.py`.

`videos/`, `output/` and `.env` are git-ignored.
