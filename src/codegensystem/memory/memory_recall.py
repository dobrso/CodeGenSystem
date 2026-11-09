import logging

from memory.long_term_memory import recall_memories


logger = logging.getLogger("codegensystem.memory")

def memory_recall_node(state):
    records = recall_memories(state["input"])

    if not records:
        return {"recall_block": ""}

    lines = []
    for r in records:
        mark = "Отклонен" if r["verdict"] == "REJECT" else "Принят"
        lines.append(
            f"[похожий запрос, сходство {r['score']:.2f}, {mark}]\n"
            f"Запрос: {r['request'][:200]}\n"
            f"План: {'; '.join(r['plan'])[:300]}"
        )

    logger.info("Произошло обращение к памяти")

    return {"recall_block": "\n\n---\n\n".join(lines)}