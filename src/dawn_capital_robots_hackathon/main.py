import hashlib
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from .analyse_frames import Verdict, analyse_frames
from .check_video import check_video
from .extract_frames import extract_frames
from .prompt import PROMPT

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
# how many videos are processed, and sent to the model, at once (1 = one at a time)
PARALLEL_VIDEOS = 5
ID_FIELDS = ("submission_id", "participant_id", "collection_id")


def load_responses(directory):
    """Map video filename -> submission/participant/collection ids, from responses.jsonl next to the videos."""
    path = directory / "responses.jsonl"
    if not path.exists():
        return {}
    meta = {}
    for line in path.read_text().splitlines():
        try:
            record = json.loads(line)
            ids = {k: record.get(k) for k in ID_FIELDS}
            for response in record["responses"].values():
                for f in response.get("files", []):
                    meta[Path(f["path"]).name] = ids
        except (ValueError, KeyError, AttributeError, TypeError):
            continue  # blank or malformed line
    return meta


def output_dir(video):
    # the stem alone collides for a.mp4 / a.mov and for x/clip.mp4 / y/clip.mp4
    digest = hashlib.sha1(str(video.resolve()).encode()).hexdigest()[:8]
    return Path("output") / f"{video.stem}-{digest}"


def process(video, prompt, ids):
    out_dir = output_dir(video)
    out_dir.mkdir(parents=True, exist_ok=True)
    # drop the previous run's results so a failed run can't leave a stale report or frames behind
    (out_dir / "report.json").unlink(missing_ok=True)
    shutil.rmtree(out_dir / "frames", ignore_errors=True)

    tests = check_video(video)
    llm = None
    if all(t["passed"] for t in tests):
        frames = extract_frames(video, out_dir / "frames")
        verdict, llm = analyse_frames(frames, prompt)
        tests += [{"test": name, **check} for name, check in verdict.items()]
    else:
        tests += [{"test": name, "passed": False, "reason": "skipped: technical checks failed"} for name in Verdict.model_fields]

    report = {**ids, "video": str(video), "passed": all(t["passed"] for t in tests), "tests": tests}
    if llm:
        report["llm"] = llm
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    return report


def run(video, meta):
    ids = meta.get(video.name) or dict.fromkeys(ID_FIELDS)
    try:
        report = process(video, PROMPT, ids)
        print(f"{'PASS' if report['passed'] else 'FAIL'}  {video}")
    except Exception as e:
        report = {**ids, "video": str(video), "passed": False, "error": str(e)}
        print(f"ERROR {video}: {e}")
    return report


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "videos")
    videos = [target] if target.is_file() else sorted(p for p in target.iterdir() if p.suffix.lower() in VIDEO_EXTS)
    meta = load_responses(target if target.is_dir() else target.parent)
    # console lines appear as videos finish; map keeps reports in input order
    with ThreadPoolExecutor(PARALLEL_VIDEOS) as pool:
        reports = list(pool.map(partial(run, meta=meta), videos))

    summary = {
        "total": len(reports),
        "passed": sum(r["passed"] for r in reports),
        "failed": sum(not r["passed"] and "error" not in r for r in reports),
        "errors": sum("error" in r for r in reports),
        "total_tokens": sum((r.get("llm") or {}).get("total_tokens") or 0 for r in reports),
    }
    Path("output").mkdir(exist_ok=True)
    (Path("output") / "report.json").write_text(json.dumps({"summary": summary, "videos": reports}, indent=2))


if __name__ == "__main__":
    main()
