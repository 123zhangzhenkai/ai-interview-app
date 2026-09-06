"""DeepSeek 直连客户端（OpenAI 兼容协议）。

MVP 阶段直连 DeepSeek 提供 AI 能力；后续如需复杂工作流可切换 services/dify_client.py。
统一处理：超时、错误降级；支持阻塞与流式两种返回。
"""
import httpx

from app.core.config import settings
from app.core.exceptions import BusinessError


class DeepSeekClient:
    def __init__(self) -> None:
        self.base_url = settings.DEEPSEEK_BASE_URL.rstrip("/")
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = settings.DEEPSEEK_TIMEOUT

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise BusinessError(code=20001, message="未配置 DeepSeek API Key，请在 .env 中设置 DEEPSEEK_API_KEY")
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def chat(
        self,
        *,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict:
        """阻塞式对话补全，返回 DeepSeek 原始响应 JSON。"""
        url = f"{self.base_url}/chat/completions"
        payload: dict = {"model": self.model, "messages": messages, "temperature": temperature}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(self, *, messages: list[dict], temperature: float = 0.7):
        """流式对话补全，逐条产出 SSE 数据行，供接口透传。"""
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "stream": True}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=self._headers()) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        yield line


deepseek_client = DeepSeekClient()
