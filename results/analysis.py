from typing import List, Dict
from datetime import datetime
import matplotlib.pyplot as plt


# =====================
# TOTAL EXECUTION TIMES
# =====================

def total_exec_time(pipelines: Dict) -> int:
    """
    Total execution time since start to finish of all pipelines.
    """
    start_timestamps = []
    finish_timestamps = []
    for pipeline in pipelines:
        scheduled_at = datetime.fromisoformat(pipeline['scheduled_at'])
        finished_at = datetime.fromisoformat(pipeline['finished_at'])
        start_timestamps.append(scheduled_at)
        finish_timestamps.append(finished_at)

    start = min(start_timestamps)
    end = max(finish_timestamps)
    delta = (end - start).total_seconds()
    return int(delta)


def total_exec_time_avg(experiments: List[Dict]) -> float:
    """
    Average of total execution time for different experiments.
    """
    exec_times = [total_exec_time(pipeline) for pipeline in experiments]
    return round(sum(exec_times) / len(exec_times), 2)


# ==========================
# INDIVIDUAL EXECUTION TIMES
# ==========================

def pipeline_exec_times(pipelines: Dict) -> Dict[str, int]:
    """
    Execution time of each individual pipeline.
    """
    execution_times = {}
    for pipeline in pipelines:
        scheduled_at = datetime.fromisoformat(pipeline['scheduled_at'])
        finished_at = datetime.fromisoformat(pipeline['finished_at'])
        delta = (finished_at - scheduled_at).total_seconds()
        execution_times[pipeline["name"]] = int(delta)

    return execution_times


def pipeline_exec_times_avg(experiments: List[Dict]) -> Dict[str, float]:
    """
    Average execution time of each individual pipeline.
    """
    avg_exec_times = {}
    for pipeline in experiments:
        exec_times = pipeline_exec_times(pipeline)
        for name, exec_time in exec_times.items():
            if name not in avg_exec_times:
                avg_exec_times[name] = []
            avg_exec_times[name].append(exec_time)

    avg_exec_times = {
        name: round(sum(times) / len(times), 2)
        for name, times in avg_exec_times.items()
    }
    return avg_exec_times


# ===================
# TOTAL WAITING TIMES
# ===================

def total_wait_time(pipelines: Dict) -> int:
    """
    Sum of all waiting times of all pipelines.
    """
    wait_times = []
    for pipeline in pipelines:
        submitted_at = datetime.fromisoformat(pipeline['submitted_at'])
        scheduled_at = datetime.fromisoformat(pipeline['scheduled_at'])
        delta = (scheduled_at - submitted_at).total_seconds()
        wait_times.append(int(delta))

    return sum(wait_times)


def total_wait_time_avg(experiments: List[Dict]) -> float:
    """
    Average of total waiting time for different experiments.
    """
    wait_times = [total_wait_time(pipeline) for pipeline in experiments]
    return round(sum(wait_times) / len(wait_times), 2)


# ==========================
# INDIVIDUAL WAITING TIMES
# ==========================

def pipeline_wait_times(pipelines: Dict):
    """
    Waiting time of each individual pipeline.
    """
    wait_times = {}
    for pipeline in pipelines:
        submitted_at = datetime.fromisoformat(pipeline['submitted_at'])
        scheduled_at = datetime.fromisoformat(pipeline['scheduled_at'])
        delta = (scheduled_at - submitted_at).total_seconds()
        wait_times[pipeline["name"]] = int(delta)
    
    return wait_times


def pipeline_wait_times_avg(experiments: List[Dict]) -> Dict[str, float]:
    """
    Average waiting time of each individual pipeline.
    """
    avg_wait_times = {}
    for pipeline in experiments:
        wait_times = pipeline_wait_times(pipeline)
        for name, wait_time in wait_times.items():
            if name not in avg_wait_times:
                avg_wait_times[name] = []
            avg_wait_times[name].append(wait_time)

    avg_wait_times = {
        name: round(sum(times) / len(times), 2)
        for name, times in avg_wait_times.items()}
    return avg_wait_times


# ====================
# SPEEDUP CALCULATIONS
# ====================

def time_reduced_perc(times: Dict[str, int|float], main_strategy: str) -> Dict[str, float]:
    """
    Calculate the percentage of time reduced relative to baseline strategies.
    """
    percentages = {}
    for strategy, time in times.items():
        if strategy != main_strategy:
            percentages[strategy] = round((times[main_strategy] - time) / time * 100, 2)
    return percentages


def time_reduced_ratio(times: Dict[str, int|float], main_strategy: str) -> Dict[str, float]:
    """
    Calculate how many times faster the main strategy is compared to baseline strategies.
    """
    ratios = {}
    for strategy, time in times.items():
        if strategy != main_strategy:
            ratios[strategy] = round(time / times[main_strategy], 2)
    return ratios
