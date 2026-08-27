# Chain Builder – delegates to reusable DeterministicPlaybookOptimizer

from typing import List, Dict, Any
from .playbook_registry import PLAYBOOKS_REGISTRY
from .optimizer import get_optimizer

class ChainBuilderError(Exception):
    """Raised for validation errors such as cycles or missing references."""

class ChainBuilder:
    def __init__(self, findings: List[Dict[str, Any]], initial_urs: float):
        self.findings = findings
        self.initial_urs = initial_urs
        self.optimizer = get_optimizer("deterministic")

    def build(self) -> Dict[str, Any]:
        opt_res = self.optimizer.optimize(PLAYBOOKS_REGISTRY, self.findings, self.initial_urs)
        
        if "error" in opt_res:
            return {
                "incidentId": "generated-fallback",
                "recommendedChain": [],
                "totalEstimatedDuration": 0.0,
                "totalEstimatedURSReduction": 0.0,
                "overallConfidence": 1.0,
                "businessImpact": 0.0,
                "reasoning": "No compatible playbooks found.",
                "ursProjection": [self.initial_urs],
            }

        recommended_chain = []
        for idx, item in enumerate(opt_res.get("executionOrder", [])):
            recommended_chain.append({
                "playbookId": item["playbookId"],
                "title": item["title"],
                "stage": f"Stage {idx + 1}",
                "dependencies": item.get("dependencies", []),
                "parallel": item["parallel"],
                "estimatedDuration": item["estimatedDuration"],
                "estimatedURSReduction": item["ursReduction"],
                "rollbackAvailable": item["rollbackAvailable"],
            })
            
        return {
            "incidentId": opt_res["incidentId"],
            "recommendedChain": recommended_chain,
            "totalEstimatedDuration": opt_res["totalEstimatedDuration"],
            "totalEstimatedURSReduction": opt_res["metrics"]["estimatedRiskReduction"],
            "overallConfidence": opt_res["overallConfidence"],
            "businessImpact": opt_res["metrics"]["optimizationGain"],
            "reasoning": opt_res["optimizationRationale"],
            "ursProjection": opt_res["ursProjection"],
            "metrics": opt_res["metrics"],
            "rejectedPlaybooks": opt_res["rejectedPlaybooks"],
            "ursBefore": opt_res["ursBefore"],
            "ursAfter": opt_res["ursAfter"],
            "dependencyGraph": opt_res["dependencyGraph"],
            "optimizationRationale": opt_res["optimizationRationale"],
            "conflictResolutionExplanation": opt_res["conflictResolutionExplanation"]
        }
