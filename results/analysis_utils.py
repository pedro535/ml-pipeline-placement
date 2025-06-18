from typing import List, Dict
from datetime import datetime

def stddev(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    return round(variance ** 0.5, 2)


# =====================
# TOTAL EXECUTION TIMES
# =====================

def total_exec_time(pipelines: List[Dict]) -> int:
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


def total_exec_time_multiple(experiments: List[List[Dict]], std=False):
    """
    Average of total execution time for multiple experiments.
    """
    exec_times = [total_exec_time(pipelines) for pipelines in experiments]
    
    if std:
        std_dev = stddev(exec_times)
        return round(sum(exec_times) / len(exec_times), 2), std_dev
    return round(sum(exec_times) / len(exec_times), 2)


# ==========================
# INDIVIDUAL EXECUTION TIMES
# ==========================

def pipeline_exec_times(pipelines: List[Dict]) -> Dict[str, int]:
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


def pipeline_exec_times_multiple(experiments: List[List[Dict]], std=False) -> Dict[str, tuple]:
    """
    Average execution time of each individual pipeline across multiple experiments.
    """
    avg_exec_times = {}
    for pipelines in experiments:
        exec_times = pipeline_exec_times(pipelines)
        for name, exec_time in exec_times.items():
            if name not in avg_exec_times:
                avg_exec_times[name] = []
            avg_exec_times[name].append(exec_time)

    for name, times in avg_exec_times.items():
        if std:
            avg_exec_times[name] = (round(sum(times) / len(times), 2), stddev(times))
        else:
            avg_exec_times[name] = round(sum(times) / len(times), 2)

    return avg_exec_times


# ===================
# TOTAL WAITING TIMES
# ===================

def total_wait_time(pipelines: List[Dict]) -> int:
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


def total_wait_time_multiple(experiments: List[List[Dict]], std=False):
    """
    Average of total waiting time for multiple experiments.
    """
    wait_times = [total_wait_time(pipelines) for pipelines in experiments]

    if std:
        std_dev = stddev(wait_times)
        return round(sum(wait_times) / len(wait_times), 2), std_dev
    return round(sum(wait_times) / len(wait_times), 2)


# ==========================
# INDIVIDUAL WAITING TIMES
# ==========================

def pipeline_wait_times(pipelines: List[Dict]):
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


def pipeline_wait_times_multiple(experiments: List[List[Dict]], std=False) -> Dict[str, List]:
    """
    Average waiting time of each individual pipeline across multiple experiments.
    """
    avg_wait_times = {}
    for pipelines in experiments:
        wait_times = pipeline_wait_times(pipelines)
        for name, wait_time in wait_times.items():
            if name not in avg_wait_times:
                avg_wait_times[name] = []
            avg_wait_times[name].append(wait_time)
            
    for name, times in avg_wait_times.items():
        if std:
            avg_wait_times[name] = (round(sum(times) / len(times), 2), stddev(times))
        else:
            avg_wait_times[name] = round(sum(times) / len(times), 2)

    return avg_wait_times


def pipeline_wait_times_avg(pipelines: List[Dict]) -> float:
    """
    Overall average waiting time for a pipeline.
    """
    wait_times = pipeline_wait_times(pipelines)
    wait_time_avg = sum(wait_times.values()) / len(wait_times)
    return round(wait_time_avg, 2)


def pipeline_wait_times_avg_multiple(experiments: List[List[Dict]], std=False):
    """
    Overall average waiting time for a pipeline across multiple experiments.
    """
    avgs = []
    for pipelines in experiments:
        wait_times = pipeline_wait_times(pipelines)
        wait_time_avg = sum(wait_times.values()) / len(wait_times)
        avgs.append(wait_time_avg)
    avg = round(sum(avgs) / len(avgs), 2)
    if std:
        return avg, stddev(avgs)
    return avg


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


# ====================
# KFP ANALYSIS METHODS
# ====================

def kfp_get_runs(data):
    """
    Get the runs from the KFP data.
    """
    runs = []
    kfp_runs = data["runs"]

    for pipeline in kfp_runs:
        name = pipeline["display_name"].split()[0].replace("-", "_")
        created_at = pipeline["created_at"]
        created_at = datetime.fromisoformat(created_at)

        scheduled_at = pipeline["scheduled_at"]
        scheduled_at = datetime.fromisoformat(scheduled_at)
        
        finished_at = pipeline["finished_at"]
        finished_at = datetime.fromisoformat(finished_at)

        runs.append({
            "name": name,
            "created_at": created_at,
            "scheduled_at": scheduled_at,
            "finished_at": finished_at,
            "duration": (finished_at - scheduled_at).total_seconds(),
        })
    return runs


def kfp_total_exec_time(runs) -> float:
    """
    Total execution time since start to finish of all pipelines (KFP).
    """
    starts = []
    ends = []
    for run in runs:
        starts.append(run["created_at"])
        ends.append(run["finished_at"])
    min_start = min(starts)
    max_end = max(ends)
    total_time = max_end - min_start
    return total_time.total_seconds()


def kfp_total_exec_time_multiple(experiments: List[Dict], std=False):
    """
    Average of total execution time for multiple KFP experiments.
    """
    total_times = [kfp_total_exec_time(runs) for runs in experiments]

    if std:
        std_dev = stddev(total_times)
        return round(sum(total_times) / len(total_times), 2), std_dev
    return round(sum(total_times) / len(total_times), 2)


def kfp_pipeline_exec_times_multiple(experiments: list, std=False) -> dict:
    """
    Average execution time of each individual pipeline across multiple KFP runs.
    """
    pipelines = {}
    for runs in experiments:
        for pipeline in runs:
            name = pipeline["name"]
            if name not in pipelines:
                pipelines[name] = []
            pipelines[name].append(pipeline["duration"])

    for name, times in pipelines.items():
        if std:
            pipelines[name] = (round(sum(times) / len(times), 2), stddev(times))
        else:
            pipelines[name] = round(sum(times) / len(times), 2)

    return pipelines
