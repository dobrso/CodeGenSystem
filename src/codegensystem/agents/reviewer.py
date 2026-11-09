import json
import logging
import time

from utils.settings import Settings
from models.schemas import ReviewerResponse
from agents.base import load_soul, load_prompt, get_structured_llm
from observability.metrics import record_metric, timed


logger = logging.getLogger("codegensystem.reviewer")

soul = load_soul(Settings.REVIEWER_SOUL)
prompt = load_prompt(Settings.REVIEWER_PROMPT)
system_prompt = f"{soul}\n\n{prompt}"

def reviewer_node(state):
    start = time.time()
    architect = state["architect_response"]
    developer = state["developer_response"]
    logger.info(
        f"Ревьюер начал работу: changes={len(developer.changes)}, "
        f"criteria={len(architect.acceptance_criteria)}"
    )

    human = (
        f"План архитектора:\n"
        f"{json.dumps(architect.model_dump(), ensure_ascii=False, indent=2)}\n\n"
        f"Интерфейсы:\n"
        f"{json.dumps([i.model_dump() for i in architect.interfaces], ensure_ascii=False, indent=2)}\n\n"
        f"Критерии приёмки:\n"
        f"{json.dumps(architect.acceptance_criteria, ensure_ascii=False, indent=2)}\n\n"
        f"Код от разработчика:\n"
        f"{json.dumps(developer.model_dump(), ensure_ascii=False, indent=2)}"
    )

    llm = get_structured_llm(
        model=Settings.REVIEWER_MODEL,
        schema=ReviewerResponse,
        base_url=Settings.OLLAMA_BASE_URL,
    )

    try:
        result: ReviewerResponse = llm.invoke([
            ("system", system_prompt),
            ("human", human),
        ])
    except Exception as e:
        logger.error(f"Ошибка в работе ревьюера: {type(e).__name__}: {e}")
        raise

    logger.info(
        f"Ревьюер завершил работу: verdict={result.verdict}, "
        f"issues={len(result.issues)}, "
        f"criteria_checks={len(result.criteria_checks)}"
    )

    criteria_total = len(architect.acceptance_criteria)
    criteria_checked = len(result.criteria_checks)
    criteria_unmet = sum(1 for c in result.criteria_checks if not c.satisfied)

    metrics = dict(state.get("metrics") or {})
    metrics["reviewer_ms"] = int((time.time() - start) * 1000)
    metrics["verdict"] = result.verdict
    metrics["issues_count"] = len(result.issues)
    metrics["criteria_checked"] = criteria_checked
    metrics["criteria_total"] = criteria_total
    metrics["criteria_unmet"] = criteria_unmet
    metrics["criteria_coverage_ok"] = criteria_checked == criteria_total

    return {
        "reviewer_response": result,
        "metrics": metrics,
    }