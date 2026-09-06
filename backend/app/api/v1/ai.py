"""AI 直连测试接口（DeepSeek）。"""
from fastapi import APIRouter

from app.schemas.ai import ChatRequest, ChatResponse
from app.schemas.common import ResponseModel
from app.services.deepseek_client import deepseek_client

router = APIRouter()


@router.post("/chat", response_model=ResponseModel[ChatResponse], summary="DeepSeek 对话（连通性测试）")
async def chat(payload: ChatRequest):
    resp = await deepseek_client.chat(
        messages=[m.model_dump() for m in payload.messages],
        temperature=payload.temperature,
    )
    choices = resp.get("choices") or []
    content = choices[0]["message"]["content"] if choices else ""
    return ResponseModel(
        data=ChatResponse(content=content, model=resp.get("model", ""), usage=resp.get("usage"))
    )
