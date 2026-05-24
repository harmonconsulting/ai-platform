from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import json

router = APIRouter()


class StreamRequest(BaseModel):
    message: str
    model: str = "qwen2.5:7b"


def ollama_stream(message: str, model: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": message,
            "stream": True
        },
        stream=True,
        timeout=300
    )

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode("utf-8"))
        token = data.get("response", "")

        if token:
            yield token


@router.post("/")
def stream_chat(req: StreamRequest):
    return StreamingResponse(
        ollama_stream(req.message, req.model),
        media_type="text/plain"
    )
