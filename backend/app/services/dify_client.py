"""Dify 统一客户端：超时、重试、流式返回、错误降级。

后端不内嵌业务 Prompt，所有 AI 逻辑（面试官、简历解析、自我介绍、润色）均在 Dify 工作流中维护，
本客户端仅传结构化参数与上下文。
"""
import httpx

from app.core.config import settings


class DifyClient:
    def __init__(self) -> None:
        self.base_url = settings.DIFY_BASE_URL.rstrip("/")
        self.api_key = settings.DIFY_API_KEY
        self.timeout = settings.DIFY_TIMEOUT
        self.max_retries = settings.DIFY_MAX_RETRIES

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def run_workflow(self, *, inputs: dict, user: str, response_mode: str = "blocking") -> dict:
        """阻塞式运行工作流，返回结构化 JSON，带重试与错误降级。"""
        url = f"{self.base_url}/v1/workflows/run"
        payload = {"inputs": inputs, "user": user, "response_mode": response_mode}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    resp = await client.post(url, json=payload, headers=self._headers())
                    resp.raise_for_status()
                    return resp.json()
                except httpx.HTTPError:
                    if attempt == self.max_retries - 1:
                        raise
        return {}

    async def run_stream(self, *, inputs: dict, user: str):
        """流式运行工作流，逐条产出 SSE 事件，供接口以 SSE 透传。"""
        url = f"{self.base_url}/v1/workflows/run"
        payload = {"inputs": inputs, "user": user, "response_mode": "streaming"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=self._headers()) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        yield line


dify_client = DifyClient()
