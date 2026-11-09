def first_pass_approval(inputs, outputs, reference_outputs):
    rev = outputs.get("reviewer_response")
    return bool(rev) and rev.get("verdict") == "APPROVE"

def empty_changes(inputs, outputs, reference_outputs):
    dev = outputs.get("developer_response")
    arch = outputs.get("architect_response")
    if not dev or not arch:
        return True
    return len(dev.get("changes", [])) == 0 and len(arch.get("plan", [])) > 0

def escalation_present(inputs, outputs, reference_outputs):
    dev = outputs.get("developer_response")
    return bool(dev and dev.get("escalation"))

def criteria_coverage(inputs, outputs, reference_outputs):
    arch = outputs.get("architect_response")
    rev = outputs.get("reviewer_response")
    if not arch or not rev:
        return False
    return len(rev.get("criteria_checks", [])) == len(arch.get("acceptance_criteria", []))

def router_accuracy(inputs, outputs, reference_outputs):
    expected = reference_outputs.get("expected_tier")
    actual = outputs.get("router_response")
    return expected == actual

def changes_non_empty(inputs, outputs, reference_outputs):
    dev = outputs.get("developer_response")
    if not dev:
        return False
    return len(dev.get("changes", [])) > 0

def verdict_matches_expected(inputs, outputs, reference_outputs):
    expected = reference_outputs.get("expected_verdict")
    actual = outputs.get("reviewer_response", {}).get("verdict")
    return expected == actual

def no_error(inputs, outputs, reference_outputs):
    return not bool(outputs.get("error"))

def elapsed_seconds(inputs, outputs, reference_outputs):
    return float(outputs.get("_elapsed_seconds", -1.0))

def cpu_time_seconds(inputs, outputs, reference_outputs):
    return float(outputs.get("_cpu_seconds", -1.0))

def peak_memory_mb(inputs, outputs, reference_outputs):
    return float(outputs.get("_peak_memory_mb", -1.0))

def completion_rate(inputs, outputs, reference_outputs):
    return 0.0 if outputs.get("error") else 1.0

def throughput_tasks_per_min(inputs, outputs, reference_outputs):
    elapsed = outputs.get("_elapsed_seconds", 0)
    if not elapsed or elapsed <= 0:
        return 0.0
    return 60.0 / elapsed

def tokens_per_task(inputs, outputs, reference_outputs):
    metrics = outputs.get("metrics") or {}
    return int(metrics.get("total_tokens", 0))

def cost_per_task_usd(inputs, outputs, reference_outputs):
    return float(outputs.get("metrics", {}).get("cost_usd", 0.0))