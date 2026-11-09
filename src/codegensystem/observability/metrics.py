import time


def record_metric(state, key, value):
    metrics = dict(state.get("metrics") or {})
    metrics[key] = value
    return {"metrics": metrics}

def timed(state, key, start):
    return record_metric(state, f"{key}_ms", int((time.time() - start) * 1000))