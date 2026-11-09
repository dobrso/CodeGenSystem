import ast
from langchain_core.tools import tool


@tool
def find_undefined_names(code):
    """Ищет имена, которые используются, но не определены."""

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Ошибка синтаксиса"

    defined = set()
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined.add(node.name)
            for arg in node.args.args:
                defined.add(arg.arg)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                defined.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)

    builtins = {
        "print", "len", "range", "int", "str", "float", "bool",
        "list", "dict", "set", "tuple", "sum", "min", "max", "abs",
        "enumerate", "zip", "sorted", "reversed", "isinstance", "type",
    }
    undefined = used - defined - builtins
    if undefined:
        return f"Не определены: {sorted(undefined)}"
    return "ОК"