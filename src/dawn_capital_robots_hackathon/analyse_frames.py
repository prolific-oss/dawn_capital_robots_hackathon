import base64

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from .prompt import PROMPT

load_dotenv()

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
    for frame in frames:
        b64 = base64.b64encode(frame.path.read_bytes()).decode()
        content.append({"type": "text", "text": f"Frame {frame.index} at t={frame.t:.2f}s:"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    response = OpenAI().chat.completions.parse(
        model=model,
        reasoning_effort=reasoning_effort,
        messages=[{"role": "user", "content": content}],
        response_format=Verdict,
    )
    return response.choices[0].message.parsed.model_dump()
