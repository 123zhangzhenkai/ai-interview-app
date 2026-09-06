"""AI 对话测试相关 schema。"""
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="角色：system / user / assistant")
    content: str = Field(..., description="内容")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="对话消息列表")
    temperature: float = Field(0.7, ge=0, le=2, description="采样温度")


class ChatResponse(BaseModel):
    content: str
    model: str
    usage: dict | None = None
