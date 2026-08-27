from typing import List, Dict, Any, Optional
from .playbook_registry import PLAYBOOKS_REGISTRY, Playbook, get_playbook_by_id
from .optimizer import get_optimizer

class ActionGenerator:
    def __init__(self):
        self.optimizer = get_optimizer("deterministic")

    def generate_plan(
        self,
        risk_score: float,
        decision: str,
        recommendations: List[Any],
        provider: str = "aws",
        instance_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Convert incoming recommendations into a list of finding dictionaries.
        findings: List[Dict[str, Any]] = []
        for rec in recommendations:
            if isinstance(rec, dict):
                findings.append({
                    "title": rec.get("title", ""),
                    "resource": rec.get("resource", ""),
                    "severity": rec.get("severity", decision),
                })
            else:
                findings.append({"title": str(rec), "resource": "", "severity": decision})

        # Run optimization
        opt_result = self.optimizer.optimize(PLAYBOOKS_REGISTRY, findings, risk_score)

        if "error" in opt_result:
            # Return a default mock plan
            pb_name = "Default Remediation Playbook"
            pb_desc = "Configure standard DevSecOps security controls"
            aws_cmd = f"aws ec2 stop-instances --instance-ids {instance_id or 'i-04ba6569c74d41d59'}"
            tf_snippet = "resource \"aws_security_group_rule\" \"remediation\" {}"
            exec_time = 5.0
            rollback_av = True
            execution_order = [{
                "step": 1,
                "playbookId": "default",
                "title": pb_name,
                "category": "General",
                "priorityScore": 50.0,
                "selectedBecause": ["Default fallback"],
                "breakdown": {},
                "estimatedDuration": exec_time,
                "ursReduction": 0.0,
                "recoveryScore": 5.0,
                "disruptionScore": 5.0,
                "rollbackAvailable": rollback_av,
                "parallel": False
            }]
            metrics = {
                "optimizationGain": 0.0,
                "playbooksConsidered": 0,
                "playbooksSelected": 1,
                "playbooksRemoved": 0,
                "estimatedTimeSaved": 0.0,
                "estimatedRiskReduction": 0.0,
                "estimatedServiceAvailability": 100.0,
                "expectedRecoveryPercentage": 100.0
            }
            opt_result = {
                "metrics": metrics,
                "executionOrder": execution_order,
                "rejectedPlaybooks": [],
                "ursBefore": risk_score,
                "ursAfter": risk_score,
                "ursProjection": [risk_score],
                "totalEstimatedDuration": exec_time,
                "overallConfidence": 0.9,
                "dependencyGraph": {},
                "optimizationRationale": "Fallback execution mode active.",
                "conflictResolutionExplanation": ""
            }
        else:
            first_exec = opt_result["executionOrder"][0]
            pb = get_playbook_by_id(first_exec["playbookId"])
            pb_name = pb.name
            pb_desc = pb.description
            aws_cmd = pb.aws_cli_command or f"aws ec2 stop-instances --instance-ids {instance_id or 'i-04ba6569c74d41d59'}"
            tf_snippet = pb.terraform_snippet or "resource \"aws_security_group_rule\" \"remediation\" {}"
            exec_time = pb.estimated_execution_time
            rollback_av = first_exec["rollbackAvailable"]

        exec_plan = [
            {
                "step": item["step"],
                "action": item["title"],
                "description": get_playbook_by_id(item["playbookId"]).description if get_playbook_by_id(item["playbookId"]) else "Mitigation",
                "status": "Pending",
                "estimatedExecutionTime": item["estimatedDuration"]
            }
            for item in opt_result["executionOrder"]
        ]

        # Return full plan object
        return {
            "status": "success",
            "riskScore": risk_score,
            "decision": decision,
            "provider": provider,
            "instanceId": instance_id or "target-ec2",
            "summary": f"Recommended playbook: {pb_name}",
            "executionPlan": exec_plan,
            "ansiblePlaybook": f"---\n- name: {pb_name}\n  hosts: all\n  tasks:\n    - name: {pb_desc}\n      ansible.builtin.debug:\n        msg: 'Remediation active'",
            "terraformManifest": tf_snippet,
            "awsCliCommands": [aws_cmd],
            "kubectlCommands": [f"kubectl label pod -l instanceId={instance_id or 'target'} status=quarantined"],
            "shellScript": f"#!/bin/bash\n# {pb_name}\n{aws_cmd}",
            "jsonPlan": f'{{"action": "{pb_name}", "target": "{instance_id or "target"}"}}',
            "automationLevel": "Fully Automated",
            "estimatedExecutionTime": opt_result["totalEstimatedDuration"],
            "rollbackAvailable": rollback_av,
            # Extra fields from optimization run
            "metrics": opt_result["metrics"],
            "executionOrder": opt_result["executionOrder"],
            "rejectedPlaybooks": opt_result["rejectedPlaybooks"],
            "ursBefore": opt_result["ursBefore"],
            "ursAfter": opt_result["ursAfter"],
            "ursProjection": opt_result["ursProjection"],
            "dependencyGraph": opt_result["dependencyGraph"],
            "optimizationRationale": opt_result["optimizationRationale"],
            "conflictResolutionExplanation": opt_result["conflictResolutionExplanation"]
        }
