def compute_progress(session) -> dict:
    """Compute progress percentage and remaining time for a session.
    Returns a dict with 'progress' (0-100) and 'remainingTime' (seconds).
    """
    if not session.startedAt:
        return {"progress": 0, "remainingTime": 0}
    elapsed = (datetime.datetime.utcnow() - session.startedAt).total_seconds()
    total_est = sum(step.get('estimatedExecutionTime', 0) for step in session.graph)
    progress = int((elapsed / total_est) * 100) if total_est > 0 else 0
    remaining = max(int(total_est - elapsed), 0)
    return {"progress": progress, "remainingTime": remaining}
