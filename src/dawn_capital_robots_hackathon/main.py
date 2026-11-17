import json
import sys
from pathlib import Path

from .analyse_frames import Verdict, analyse_frames
from .check_video import check_video
from .extract_frames import extract_frames
from .prompt import PROMPT

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def process(video, prompt):
    out_dir = Path("output") / video.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    tests = check_video(video)
    if all(t["passed"] for t in tests):
        frames = extract_frames(video, out_dir / "frames")
        verdict = analyse_frames(frames, prompt)
        tests += [{"test": name, **check} for name, check in verdict.items()]
    else:
        tests += [{"test": name, "passed": False, "reason": "skipped: technical checks failed"} for name in Verdict.model_fields]

    report = {"video": str(video), "passed": all(t["passed"] for t in tests), "tests": tests}
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    return report


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "videos")
    videos = [target] if target.is_file() else sorted(p for p in target.iterdir() if p.suffix.lower() in VIDEO_EXTS)
    reports = []
    for video in videos:
        try:
            report = process(video, PROMPT)
            print(f"{'PASS' if report['passed'] else 'FAIL'}  {video}")
        except Exception as e:
            report = {"video": str(video), "passed": False, "error": str(e)}
            print(f"ERROR {video}: {e}")
        reports.append(report)

    summary = {
        "total": len(reports),
        "passed": sum(r["passed"] for r in reports),
        "failed": sum(not r["passed"] and "error" not in r for r in reports),
        "errors": sum("error" in r for r in reports),
    }
    Path("output").mkdir(exist_ok=True)
    (Path("output") / "report.json").write_text(json.dumps({"summary": summary, "videos": reports}, indent=2))


if __name__ == "__main__":
    main()
