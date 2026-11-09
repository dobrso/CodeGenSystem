import logging
import sys

from workflow.graph import build_graph
from memory.long_term_memory import init_memory_db
from observability.logs import setup_logging


setup_logging("INFO")
logger = logging.getLogger("codegensystem.main")


if __name__ == "__main__":
    init_memory_db()
    graph = build_graph()

    user_input = " ".join(sys.argv[1:]).strip() or input("Введите запрос: ").strip()
    if not user_input:
        logger.error("Пустой запрос")
        sys.exit(1)

    logger.info(f"Вход: {user_input}")
    result = graph.invoke({"input": user_input})
    logger.info(f"Оценка: {result.get('reviewer_response').verdict if result.get('reviewer_response') else 'N/A'}")

    if result["reviewer_response"].verdict == "APPROVED":
        print(result["developer_response"])