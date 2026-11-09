import os
from pathlib import Path


class Settings:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    SKILLS_DIR = PROJECT_ROOT / "skills"
    SOULS_DIR = PROJECT_ROOT / "souls"

    ARCHITECT_PROMPT = "architect_prompt.md"
    DEVELOPER_PROMPT = "developer_prompt.md"
    REVIEWER_PROMPT = "reviewer_prompt.md"

    ARCHITECT_SOUL = "architect_soul.md"
    DEVELOPER_SOUL = "developer_soul.md"
    REVIEWER_SOUL = "reviewer_soul.md"

    TDD_IMPLEMENTATION_SKILL = "tdd_implementation.md"

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    ARCHITECT_MODEL = "qwen3.5:2b"
    ROUTER_MODEL = "laya"
    DEVELOPER_MODEL_SMALL = "qwen3.5:2b"
    DEVELOPER_MODEL_LARGE = "qwen3.5:4b"
    REVIEWER_MODEL = "gemma3:1b"
    EMBEDDING_MODEL = "nomic-embed-text"

    MAX_INPUT_LEN = 2000

    TOP_K = 3
    MIN_SCORE = 0.35

    TIMEOUT = 20