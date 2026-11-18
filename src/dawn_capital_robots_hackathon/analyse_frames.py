import base64

from openai import OpenAI
from pydantic import BaseModel

from .prompt import PROMPT
from .settings import get_settings

MODEL = "gpt-6.1-terra"
REASONING_EFFORT = "low"


class Check(BaseModel):
    reason: str
    passed: bool


class PrivacyIssue(BaseModel):
    t: float
    description: str


class PrivacyCheck(BaseModel):
    reason: str
    issues: list[PrivacyIssue]
    passed: bool


class Verdict(BaseModel):
    stable_camera: Check
    plug_and_socket_visible: Check
    privacy_safe: PrivacyCheck


def analyse_frames(frames, prompt=PROMPT, model=MODEL, reasoning_effort=REASONING_EFFORT):
    content = [{"type": "text", "text": prompt}]
    payload_bytes = 0
    for frame in frames:
        b64 = base64.b64encode(frame.path.read_bytes()).decode()
        payload_bytes += len(b64)
        content.append({"type": "text", "text": f"Frame {frame.index} at t={frame.t:.2f}s:"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    response = OpenAI(api_key=get_settings().openai_api_key.get_secret_value()).chat.completions.parse(
        model=model,
        reasoning_effort=reasoning_effort,
        messages=[{"role": "user", "content": content}],
        response_format=Verdict,
    )
    choice = response.choices[0]
    if choice.message.refusal:
        raise ValueError(f"Model refused to analyse the frames: {choice.message.refusal}")
    if choice.message.parsed is None:
        # e.g. finish_reason "length" when the output was cut off
        raise ValueError(f"Model returned no verdict (finish_reason={choice.finish_reason})")
    usage = response.usage
    llm = {
        "model": model,
        "frames": len(frames),
        "payload_mb": round(payload_bytes / 1e6, 1),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "total_tokens": usage.total_tokens if usage else None,
    }
    return choice.message.parsed.model_dump(), llm
