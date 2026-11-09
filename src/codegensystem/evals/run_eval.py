import os
import time

import psutil
from langsmith import evaluate, traceable

from evals.dataset import dataset
from evals.evaluators import (
    first_pass_approval, empty_changes, escalation_present,
    criteria_coverage, router_accuracy,
    changes_non_empty, verdict_matches_expected,
    no_error, elapsed_seconds, cpu_time_seconds, peak_memory_mb,
    completion_rate, throughput_tasks_per_min,
    tokens_per_task, cost_per_task_usd,
)
from workflow.graph import build_graph


@traceable
def run_graph(inputs):
    graph = build_graph()
    process = psutil.Process(os.getpid())

    cpu_before = process.cpu_times()
    mem_before = process.memory_info().rss
    start = time.time()

    result = graph.invoke({"input": inputs["input"]})

    elapsed = time.time() - start
    cpu_after = process.cpu_times()
    mem_after = process.memory_info().rss

    cpu_seconds = (
        (cpu_after.user - cpu_before.user)
        + (cpu_after.system - cpu_before.system)
    )
    peak_memory_mb_val = max(mem_before, mem_after) / 1024 / 1024

    architect = result.get("architect_response")
    developer = result.get("developer_response")
    reviewer = result.get("reviewer_response")

    return {
        "architect_response": architect.model_dump() if architect else None,
        "developer_response": developer.model_dump() if developer else None,
        "reviewer_response": reviewer.model_dump() if reviewer else None,
        "router_response": result.get("router_response"),
        "output": result.get("output"),
        "metrics": result.get("metrics", {}),
        "error": result.get("error"),
        "_elapsed_seconds": elapsed,
        "_cpu_seconds": cpu_seconds,
        "_peak_memory_mb": peak_memory_mb_val,
    }


if __name__ == "__main__":
    results = evaluate(
        run_graph,
        data="codegen-system-eval",
        evaluators=[
            first_pass_approval, empty_changes, escalation_present,
            criteria_coverage, router_accuracy,
            changes_non_empty, verdict_matches_expected,
            no_error, elapsed_seconds, cpu_time_seconds, peak_memory_mb,
            completion_rate, throughput_tasks_per_min,
            tokens_per_task, cost_per_task_usd,
        ],
        experiment_prefix="codegen-baseline",
    )
    print(results)