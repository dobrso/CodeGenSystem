import ast
from langchain_core.tools import tool


@tool
def validate_python_syntax(code):
    """Проверяет синтаксис Python-кода"""

    try:
        ast.parse(code)
        return "ОК"
    except SyntaxError as e:
        return f"Ошибка синтаксиса: {e.msg} на строке {e.lineno}"