from typing import Dict, Any
import datetime


def generate_report(session) -> Dict[str, Any]:
    """Generate a execution report dict (JSON) from a session.
    Includes playbook chain, timestamps, logs, API calls, verification evidence, URS stats, and status.
    """
    report = {
        "executionId": session.executionId,
        "operator": session.operator,
        "status": session.status,
        "startedAt": session.startedAt.isoformat() + "Z" if session.startedAt else None,
        "completedAt": session.completedAt.isoformat() + "Z" if session.completedAt else None,
        "ursBefore": session.ursBefore,
        "ursAfter": session.ursAfter,
        "riskReduction": session.riskReduction,
        "playbookChain": [step.get("playbookId") for step in session.graph],
        "totalSteps": len(session.graph),
        "logs": session.logs,
        "auditTrail": session.auditTrail,
        "awsApiCalls": session.awsApiCalls,
        "verificationResults": session.verificationResult,
        "rollbackAvailable": session.rollbackAvailable,
        "rollbackExecuted": session.rollbackExecuted,
    }
    return report
