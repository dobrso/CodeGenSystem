import logging
import time

import httpx

from utils.settings import Settings
from observability.metrics import record_metric, timed


logger = logging.getLogger("codegensystem.router")

COMPLEX_ALGO_MARKERS = (
    "algorithm", "sort", "graph", "tree", "dynamic", "parse",
    "recurs", "binary", "hash", "traversal", "dijkstra", "bfs", "dfs",
)

EDGE_CASE_MARKERS = (
    "empty", "duplicate", "boundary", "edge", "null", "none",
    "overflow", "underflow", "invalid", "negative", "zero",
)

def has_complex_algorithm(architect):
    text = " ".join(architect.plan).lower()
    return any(m in text for m in COMPLEX_ALGO_MARKERS)

def has_edge_cases(architect):
    text = " ".join(architect.acceptance_criteria).lower()
    return any(m in text for m in EDGE_CASE_MARKERS)

def build_router_state(state, architect):
    files_gt_two = len(architect.files) > 2
    has_algo = has_complex_algorithm(architect)
    has_open = bool(architect.open_questions)
    criteria_gt_five = len(architect.acceptance_criteria) > 5
    has_edges = has_edge_cases(architect)

    lines = [
        f"Запрос пользователя: {state['input']}",
        "",
        "План архитектора:",
        f"- Больше двух файлов: {'да' if files_gt_two else 'нет'}",
        f"- Содержит тяжелые алгоритмы и структуры данных: {'да' if has_algo else 'нет'}",
        f"- Есть открытые вопросы: {'да' if has_open else 'нет'}",
        f"- Больше пяти критериев приемки: {'да' if criteria_gt_five else 'нет'}",
        f"- Критерии приемки содержат граничные случаи: {'да' if has_edges else 'нет'}",
    ]
    return "\n".join(lines)

def router_node(state):
    start = time.time()
    architect = state["architect_response"]

    logger.info(
        f"Роутер начал работу: files={len(architect.files)}, "
        f"criteria={len(architect.acceptance_criteria)}, "
        f"open_questions={len(architect.open_questions)}"
    )

    payload = {
        "model": Settings.ROUTER_MODEL,
        "state": build_router_state(state, architect),
        "questions": {
            "model_tier": {
                "type": "choice",
                "instructions": (
                    "Выбери модель для разработчика. "
                    "Если ХОТЯ БЫ ОДИН сигнал 'да' — выбери LARGE. "
                    "Если ВСЕ сигналы 'нет' — выбери SMALL. "
                    "Если не можешь решить, то выбирай LARGE."
                ),
                "criteria": {
                    "SMALL": (
                        "ВСЕ сигналы 'нет': не больше двух файлов, "
                        "нет тяжелых алгоритмов, нет открытых вопросов, "
                        "не более пяти критериев приемки, "
                        "нет граничных случаев в критериях приемки."
                    ),
                    "LARGE": (
                        "ХОТЯ БЫ ОДИН сигнал 'да': больше двух файлов, "
                        "присутствуют тяжелые алгоритмы, существуют открытые вопросы, "
                        "больше пяти критериев приемки, "
                        "или присутствуют граничные случаи в критериях приемки."
                    ),
                },
            }
        },
    }

    try:
        response = httpx.post(
            f"{Settings.OLLAMA_BASE_URL}/v1/systemone",
            json=payload,
            timeout=Settings.TIMEOUT,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Ошибка в работе роутера: {type(e).__name__}: {e}")
        return {
            "router_response": "SMALL",
            **timed(state, "router", start),
            **record_metric(state, "router_fallback", True),
            **record_metric(state, "router_error", str(e)),
        }

    data = response.json()
    decision = data["answers"]["model_tier"]["choice"]

    logger.info(f"Решение роутера: {decision}")

    metrics = dict(state.get("metrics") or {})
    metrics["router_ms"] = int((time.time() - start) * 1000)
    metrics["router_decision"] = decision
    metrics["router_fallback"] = False

    return {
        "router_response": decision,
        "metrics": metrics,
    }