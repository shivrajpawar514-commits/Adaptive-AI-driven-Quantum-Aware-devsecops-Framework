from typing import Tuple
import datetime


def rollback_playbook(session, playbook) -> Tuple[bool, str]:
    """Execute the rollback command for a playbook.
    For the demo, we just log the rollback command and mark success.
    Returns a tuple (success, message).
    """
    if not playbook.rollback:
        return False, "No rollback defined for this playbook"
    # Simulate execution – in real implementation this would invoke safe boto3 or CLI.
    message = f"Executed rollback for playbook {playbook.id}: {playbook.rollback}"
    session.add_log(message)
    # Record a fake API call entry for consistency
    session.record_api_call(
        api_name="RollbackCommand",
        http_status=200,
        request_id="rollback-" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        duration_ms=50,
        outcome="Success",
    )
    return True, message
