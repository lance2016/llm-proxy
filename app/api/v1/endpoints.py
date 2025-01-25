import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Union

from app.core.exceptions import LLMAPIException
from app.schemas.base import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat.service import ChatService
from app.core.context import request_id_var

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    fastapi_request: Request,
) -> Union[ChatCompletionResponse, StreamingResponse]:
    """Create a chat completion"""
    try:
        trace_id = request_id_var.get()
        logger.info(
            f"Received request: {request.model_dump_json()}",
            extra={"trace_id": trace_id}
        )
        response = await ChatService.chat_completion(request)
        if request.stream:
            return StreamingResponse(
                response,
                media_type="text/event-stream"
            )
        return response
    except LLMAPIException as e:
        logger.error(
            f"LLM API error: {e.detail}",
            extra={"trace_id": trace_id}
        )
        raise e
    except Exception as e:
        logger.exception(
            "Unexpected error in chat completion",
            extra={"trace_id": trace_id}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 