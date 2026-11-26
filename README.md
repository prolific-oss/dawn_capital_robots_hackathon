# Dawn Capital Robots Hackathon

A video quality gate for robot demonstration footage. It checks that a video of a plug being inserted into a socket is good enough to use, for example as training data.

Each video goes through two stages:

1. **Technical checks** (OpenCV)
   - `min_fps_30` / `max_fps_60`: between 30 and 60 fps. The minimum is nominal, so 29.0 passes ("30 fps" phone footage often reports 29.3–30.1); 60.1 is the matching tolerance on the maximum.
   - `min_resolution_720p` / `max_resolution_2160p`: the shorter side is between 720 and 2160 px.
   - `max_duration_30s`: at most 30 seconds, which bounds the number of frames sent to the model.
   - `min_duration_4s`: at least 4 seconds, the shortest clip in the sample data with a complete plug-in.
2. **Visual checks** (OpenAI vision model). These run only if the technical checks pass.
   - `stable_camera`: the camera doesn't shake, pan, tilt or zoom.
   - `plug_and_socket_visible`: the plug and socket are in frame, in focus, well lit and not blocked.
   - `privacy_safe`: no frame shows a face, readable personal text, a photo or screen of a person, or a distinctive tattoo, scar or birthmark. Each problem is listed under `issues` with its timestamp. Ordinary hands, arms, clothing and plain jewellery are allowed, and so is printed text on clothing or products (slogans, brand names) unless it names a person. The policy is in `prompt.py`; edit it there. Audio is not checked.

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
| `settings.py` | Loads the OpenAI API key (pydantic-settings). |

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
cp .env.example .env   # then put your OpenAI API key in .env
```

The key is read from `.env` in the directory you run from. A real `OPENAI_API_KEY` environment variable takes precedence. If neither is set, the run stops with a clear error when the first model call is made.

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

For each video, `output/<video-name>-<hash>/` contains (the hash is derived from the video's full path, so videos with the same name don't overwrite each other):

- `frames/`: the sampled frames (`frame_000000.jpg`, `frame_000005.jpg`, ... named by source frame index).
- `report.json`: the overall result and each check's result.

Frames and `report.json` from a previous run are deleted when the video is processed again.

A combined `output/report.json` covers every video in the run: a `summary` (total, passed, failed, errors, total_tokens) and a `videos` list holding each video's report (or an `error` message if processing crashed).

```json
{
  "video": "videos/example1.mov",
  "passed": true,
  "tests": [
    {"test": "min_fps_30", "passed": true, "value": 30.0},
    {"test": "max_fps_60", "passed": true, "value": 30.0},
    {"test": "min_resolution_720p", "passed": true, "value": "1920x1080"},
    {"test": "max_resolution_2160p", "passed": true, "value": "1920x1080"},
    {"test": "min_duration_4s", "passed": true, "value": "12.0s"},
    {"test": "max_duration_30s", "passed": true, "value": "12.0s"},
    {"test": "stable_camera", "passed": true, "reason": "..."},
    {"test": "plug_and_socket_visible", "passed": true, "reason": "..."},
    {"test": "privacy_safe", "passed": true, "reason": "...", "issues": []}
  ]
}
```

Videos that reach the model also get an `llm` block with the model name, the number of frames sent, the upload size (`payload_mb`) and the token counts the API reported, so you can see what each video costs:

```json
"llm": {"model": "gpt-6.1-terra", "frames": 53, "payload_mb": 24.9, "prompt_tokens": 61000, "completion_tokens": 900, "total_tokens": 61900}
```

Videos rejected by the technical checks make no API call and have no `llm` block.

## Customising

- **Model and reasoning effort**: set `MODEL` and `REASONING_EFFORT` in `src/dawn_capital_robots_hackathon/analyse_frames.py`.
- **Prompt or criteria**: edit `src/dawn_capital_robots_hackathon/prompt.py`. If you add a check, add a matching field to `Verdict` in `src/dawn_capital_robots_hackathon/analyse_frames.py`.
- **Sampling rate**: change `FRAME_STEP` (keep every Nth frame) in `src/dawn_capital_robots_hackathon/extract_frames.py`.
- **Thresholds**: change the FPS and resolution limits in `src/dawn_capital_robots_hackathon/check_video.py`.

`videos/`, `output/` and `.env` are git-ignored.

## License

[MIT](LICENSE)
