"""全局配置:从 .env 读取,集中管理路径、AI 方案与检索参数。

只在这里读环境变量,业务代码一律从 `settings` 取值,方便方案 A/B 切换与部署调参。
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ 目录,作为相对路径基准
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- AI 方案切换(命脉)----
    # 取值:openai / zhipu / dashscope —— 三家均走 OpenAI 兼容端点
    ai_provider: str = "zhipu"

    # 方案 A:OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    # 方案 B-1:智谱 GLM(开发默认)
    zhipu_api_key: str = ""
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    zhipu_embedding_model: str = "embedding-3"
    zhipu_chat_model: str = "glm-4-flash"

    # 方案 B-2:阿里 DashScope(通义)
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_embedding_model: str = "text-embedding-v3"
    dashscope_chat_model: str = "qwen-plus"

    # ---- 存储路径(部署时挂 volume 持久化)----
    sqlite_path: Path = BASE_DIR / "data" / "app.db"
    chroma_path: Path = BASE_DIR / "data" / "chroma_db"
    upload_dir: Path = BASE_DIR / "data" / "uploads"

    # ---- 检索 / 切块参数 ----
    top_k: int = 4
    chunk_size: int = 500
    chunk_overlap: int = 50

    # ---- CORS(前端 dev 源)----
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ---- 按当前 provider 解析出实际使用的 key/base_url/模型名 ----
    @property
    def active_api_key(self) -> str:
        return getattr(self, f"{self.ai_provider}_api_key")

    @property
    def active_base_url(self) -> str:
        return getattr(self, f"{self.ai_provider}_base_url")

    @property
    def active_embedding_model(self) -> str:
        return getattr(self, f"{self.ai_provider}_embedding_model")

    @property
    def active_chat_model(self) -> str:
        return getattr(self, f"{self.ai_provider}_chat_model")

    def ensure_dirs(self) -> None:
        """确保运行期目录存在(数据库 / Chroma / 上传)。"""
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
