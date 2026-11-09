import logging
import json
import time

from memory.long_term_memory import persist_memory
from observability.metrics import record_metric, timed


logger = logging.getLogger("codegensystem.output")

def output_node(state):
    start = time.time()
    review = state.get("reviewer_response")
    if review is None:
        return {"output": "Нет результата ревью"}

    memory_saved = False
    try:
        persist_memory(state)
        memory_saved = True
        logger.info(f"Сохранено: verdict={review.verdict}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении: {type(e).__name__}: {e}")

    metrics = dict(state.get("metrics") or {})
    metrics["output_ms"] = int((time.time() - start) * 1000)
    metrics["memory_saved"] = memory_saved
    metrics["final_verdict"] = review.verdict

    return {
        "output": json.dumps(review.model_dump(), ensure_ascii=False, indent=2),
        "metrics": metrics,
    }