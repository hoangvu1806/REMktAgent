from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.content_creator.coordinator import root_agent


router = APIRouter(prefix="/agents", tags=["agents"])

APP_NAME = "content_creator_app"

session_service = InMemorySessionService()

runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
)

_RUN_CONFIG = RunConfig(streaming_mode=StreamingMode.SSE)


class ChatStreamRequest(BaseModel):
    user_id: str
    session_id: str
    message: str


@router.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest) -> StreamingResponse:
    async def event_generator():
        try:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=req.user_id,
                session_id=req.session_id,
            )
        except AlreadyExistsError:
            # Reuse the existing session for subsequent messages in the same turn.
            pass

        content = types.Content(
            role="user",
            parts=[types.Part(text=req.message)],
        )

        async for event in runner.run_async(
            user_id=req.user_id,
            session_id=req.session_id,
            new_message=content,
            run_config=_RUN_CONFIG,
        ):
            if not event.content or not event.content.parts:
                continue

            texts = [
                part.text
                for part in event.content.parts
                if getattr(part, "text", None)
            ]
            if not texts:
                continue

            payload = {
                "author": getattr(event, "author", None),
                "type": "agent_event",
                "partial": getattr(event, "partial", False),
                "text": "".join(texts),
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            # Yield control so the event loop flushes the chunk to the client
            # before processing the next ADK event.
            await asyncio.sleep(0)

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
