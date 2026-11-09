from langchain_ollama import ChatOllama

from utils.settings import Settings


def load_prompt(filename):
    path = Settings.PROMPTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(path)

    return path.read_text(encoding="utf-8")

def load_skill(filename):
    path = Settings.SKILLS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(path)

    return path.read_text(encoding="utf-8")

def load_soul(filename):
    path = Settings.SOULS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(path)

    return path.read_text(encoding="utf-8")

def get_structured_llm(model, schema, base_url):
    llm = ChatOllama(model=model, base_url=base_url)

    return llm.with_structured_output(schema, method="json_schema")
