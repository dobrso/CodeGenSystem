import importlib.util

import ast
from langchain_core.tools import tool


@tool
def check_imports(code):
    """Проверяет, что все импортированные модули доступны в текущем окружении."""

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Ошибка синтаксиса"

    missing = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if importlib.util.find_spec(name) is None:
                    missing.append(name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            name = node.module.split(".")[0]
            if importlib.util.find_spec(name) is None:
                missing.append(name)

    if missing:
        return f"Отсутствуют модули: {sorted(set(missing))}"
    return "ОК"