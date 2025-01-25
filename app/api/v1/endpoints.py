from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.base import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatCompletionStreamResponse
)
from app.utils.provider import get_provider_by_model
from typing import Union
import json

router = APIRouter()

async def stream_response(generator):
    try:
        async for chunk in generator:
            if isinstance(chunk, ChatCompletionStreamResponse):
                yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/chat/completions",
    response_model=Union[ChatCompletionResponse, ChatCompletionStreamResponse]
)
async def create_chat_completion(request: ChatCompletionRequest):
    try:
        provider = get_provider_by_model(request.model)
        
        if request.stream:
            return StreamingResponse(
                stream_response(provider.chat_completion_stream(request)),
                media_type="text/event-stream",
                background=provider.close
            )
        else:
            async with provider:
                return await provider.chat_completion(request)
                
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 