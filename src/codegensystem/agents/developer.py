import json
import logging
import time

from utils.settings import Settings
from models.schemas import DeveloperResponse
from agents.base import load_soul, load_prompt, load_skill, get_structured_llm
from tools.python_syntax import validate_python_syntax
from tools.undefined_names import find_undefined_names
from tools.importing import check_imports
from observability.metrics import record_metric, timed


logger = logging.getLogger("codegensystem.developer")

soul = load_soul(Settings.DEVELOPER_SOUL)
prompt = load_prompt(Settings.DEVELOPER_PROMPT)
skill = load_skill(Settings.TDD_IMPLEMENTATION_SKILL)
system_prompt = f"{soul}\n\n{prompt}\n\n{skill}"

def developer_node(state):
    start = time.time()
    architect = state["architect_response"]
    decision = state["router_response"]
    model = (
        Settings.DEVELOPER_MODEL_LARGE
        if decision == "LARGE"
        else Settings.DEVELOPER_MODEL_SMALL
    )
    logger.info(f"Разработчик начал работу: model={model}, open_questions={len(architect.open_questions)}")

    human = (
        f"Запрос пользователя:\n{state['input']}\n\n"
        f"Ответ архитектора:\n{json.dumps(architect.model_dump(), ensure_ascii=False, indent=2)}"
    )

    llm = get_structured_llm(
        model=model,
        schema=DeveloperResponse,
        base_url=Settings.OLLAMA_BASE_URL,
    )

    try:
        result = llm.invoke([("system", system_prompt),("human", human),])
    except Exception as e:
        logger.error(f"Ошибка разработчика: {type(e).__name__}: {e}")
        raise

    static_problems = 0
    if result.changes and not result.escalation:
        problems = []
        for change in result.changes:
            if not change.path.endswith(".py"):
                continue

            syntax = validate_python_syntax.invoke({"code": change.content})
            if syntax != "OK":
                logger.warning(f"Ошибка синтаксиса {change.path}")
                problems.append(f"{change.path}")
                continue

            imports = check_imports.invoke({"code": change.content})
            if imports != "OK":
                logger.warning(f"Ошибка импорта {change.path}: {imports}")
                problems.append(f"{change.path}: {imports}")

            undefined = find_undefined_names.invoke({"code": change.content})
            if undefined != "OK":
                logger.warning(f"Ошибка переменных {change.path}: {undefined}")
                problems.append(f"{change.path}: {undefined}")

        static_problems = len(problems)
        if problems:
            result.escalation = problems
            result.notes = "Статический анализ нашёл проблемы до запуска в sandbox."
            logger.warning(f"Разработчик нашел проблемы: {len(problems)}")

    if architect.open_questions and not result.escalation:
        result.escalation = [f"open_questions не пуст: {q}" for q in architect.open_questions]
        logger.warning("Разработчик эскариловал открытые вопросы")

    logger.info(
        f"Разработчик завершил работу: changes={len(result.changes)}, "
        f"escalation={len(result.escalation)}"
    )

    metrics = dict(state.get("metrics") or {})
    metrics["developer_ms"] = int((time.time() - start) * 1000)
    metrics["developer_model"] = model
    metrics["developer_changes"] = len(result.changes)
    metrics["developer_escalation"] = len(result.escalation)
    metrics["static_problems"] = static_problems

    return {
        "developer_response": result,
        "metrics": metrics,
    }