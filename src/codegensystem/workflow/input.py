import logging

from utils.settings import Settings


logger = logging.getLogger("codegensystem.input")

def input_node(state):
    text = (state.get("input") or "").strip()
    if not text:
        logger.error("Input пуст")
        raise ValueError("input пуст")
    if len(text) > Settings.MAX_INPUT_LEN:
        logger.error(f"Input rejected: {len(text)} chars > {Settings.MAX_INPUT_LEN}")
        raise ValueError(f"input длиннее {Settings.MAX_INPUT_LEN} символов")

    logger.info(f"На вход подано {len(text)} символов")
    return {"input": text}