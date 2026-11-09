import logging
import time

from utils.settings import Settings
from models.schemas import ArchitectResponse
from agents.base import load_soul, load_prompt, get_structured_llm
from observability.metrics import record_metric, timed


logger = logging.getLogger("codegensystem.architect")

soul = load_soul(Settings.ARCHITECT_SOUL)
prompt = load_prompt(Settings.ARCHITECT_PROMPT)
system_prompt = f"{soul}\n\n{prompt}"

def architect_node(state):
    start = time.time()
    logger.info("Архитектор начал работу")

    llm = get_structured_llm(
        model=Settings.ARCHITECT_MODEL,
        schema=ArchitectResponse,
        base_url=Settings.OLLAMA_BASE_URL,
    )

    human = state["input"]
    block = state.get("recall_block") or ""
    recall_used = bool(block)
    if block:
        logger.debug(f"Архитектор обратился к памяти: {len(block)} символов")
        human = (
            "Похожие прошлые запросы:\n\n"
            f"{block}\n\n---\n\nТекущий запрос:\n{human}"
        )

    try:
        result = llm.invoke([("system", system_prompt), ("human", human)])
    except Exception as e:
        logger.error(f"Ошибка в работе архитектора: {type(e).__name__}: {e}")
        raise

    logger.info(
        f"Архитектор завершил работу: files={len(result.files)}, "
        f"interfaces={len(result.interfaces)}, "
        f"criteria={len(result.acceptance_criteria)}, "
        f"open_questions={len(result.open_questions)}"
    )

    metrics = dict(state.get("metrics") or {})
    metrics["architect_ms"] = int((time.time() - start) * 1000)
    metrics["architect_files"] = len(result.files)
    metrics["architect_interfaces"] = len(result.interfaces)
    metrics["architect_criteria"] = len(result.acceptance_criteria)
    metrics["architect_open_questions"] = len(result.open_questions)
    metrics["recall_used"] = recall_used

    return {
        "architect_response": result,
        "metrics": metrics,
    }