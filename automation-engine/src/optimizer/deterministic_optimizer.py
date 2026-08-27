import uuid
import itertools
from datetime import datetime
from typing import List, Dict, Any, Set

from .base import BaseOptimizer
from ..playbook_registry import Playbook, get_playbook_by_id
from ..service_config import SCORING_WEIGHTS, SEVERITY_WEIGHTS, POLICY_PRIORITY_WEIGHTS

class DeterministicPlaybookOptimizer(BaseOptimizer):
    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Deterministic Playbook Optimization Engine",
            "version": "1.0",
            "type": "Rule Based",
            "deterministic": True,
            "explainable": True,
            "requiresTraining": False
        }

    def score_playbook(self, playbook: Playbook, current_urs: float, max_finding_severity: str) -> Dict[str, Any]:
        # Resolve weights from config
        w_sev = SCORING_WEIGHTS.get("severity", 2.0)
        w_urs = SCORING_WEIGHTS.get("urs", 0.3)
        w_rec = SCORING_WEIGHTS.get("recovery", 2.5)
        w_pol = SCORING_WEIGHTS.get("policy_priority", 2.0)
        w_conf = SCORING_WEIGHTS.get("confidence", 5.0)
        w_dis = SCORING_WEIGHTS.get("disruption", -1.5)
        w_time = SCORING_WEIGHTS.get("execution_time", -0.1)

        # Get weights values
        sev_val = max((SEVERITY_WEIGHTS.get(s.lower(), 0) for s in playbook.severity), default=0)
        pol_val = POLICY_PRIORITY_WEIGHTS.get(playbook.execution_priority.lower(), 2)

        # Calculate factors
        f_sev = w_sev * sev_val
        f_urs = w_urs * current_urs
        f_rec = w_rec * playbook.recovery_score
        f_pol = w_pol * pol_val
        f_conf = w_conf * playbook.confidence
        f_dis = w_dis * playbook.disruption_score
        f_time = w_time * playbook.estimated_execution_time

        # Calculate final priority score
        total_score = round(f_sev + f_urs + f_rec + f_pol + f_conf + f_dis + f_time, 2)

        # Determine explainability list
        selected_because = []
        if playbook.recovery_score >= 8.0:
            selected_because.append("Highest recovery score")
        if "critical" in [s.lower() for s in playbook.severity] or playbook.execution_priority.lower() == "critical":
            selected_because.append("Critical severity")
        if playbook.disruption_score <= 2.0:
            selected_because.append("Low disruption")
        if playbook.rollback:
            selected_because.append("Supports rollback")
        if playbook.confidence >= 0.9:
            selected_because.append("High confidence decision")
        if not selected_because:
            selected_because.append("Best matching baseline mitigation")

        score_breakdown = {
            "priorityScore": total_score,
            "selectedBecause": selected_because,
            "scoreBreakdown": {
                "severity": round(f_sev, 2),
                "urs": round(f_urs, 2),
                "recovery": round(f_rec, 2),
                "policy": round(f_pol, 2),
                "confidence": round(f_conf, 2),
                "disruptionPenalty": round(f_dis, 2),
                "executionPenalty": round(f_time, 2),
                "finalScore": total_score
            }
        }
        return score_breakdown

    def _matches(self, playbook: Playbook, finding: Dict[str, Any]) -> bool:
        title = str(finding.get("title", "")).lower()
        resource = str(finding.get("resource", "")).lower()
        for pattern in playbook.supported_findings:
            if pattern.lower() in title:
                if not resource or not playbook.supported_resources or any(
                    r.lower() == resource for r in playbook.supported_resources
                ):
                    return True
        return False

    def optimize(self, playbooks: List[Playbook], findings: List[Dict[str, Any]], current_urs: float) -> Dict[str, Any]:
        playbook_lookup = {pb.id: pb for pb in playbooks}

        # 1. Filter compatible playbooks matching the active findings
        compatible: List[Playbook] = []
        for pb in playbooks:
            if any(self._matches(pb, f) for f in findings):
                compatible.append(pb)

        # Record considered count
        playbooks_considered = len(compatible)

        if not compatible:
            return {"error": "No compatible playbooks found"}

        # Determine finding severity context
        finding_severities = [f.get("severity", "medium").lower() for f in findings]
        max_severity = "critical" if "critical" in finding_severities else "high" if "high" in finding_severities else "medium"

        # 2. Score all compatible candidates deterministically
        scored_candidates = []
        for pb in compatible:
            score_data = self.score_playbook(pb, current_urs, max_severity)
            scored_candidates.append({
                "playbook": pb,
                "score_data": score_data
            })

        # 3. Sort candidates by Priority Score descending
        scored_candidates.sort(key=lambda x: x["score_data"]["priorityScore"], reverse=True)

        # 4. Deduplicate playbooks addressing same findings/categories and resolve conflicts
        selected_candidates = []
        selected_ids = set()
        rejected_playbooks = []

        for item in scored_candidates:
            pb = item["playbook"]
            score = item["score_data"]["priorityScore"]

            # Conflict resolution
            has_conflict = False
            for conf_id in pb.conflicts:
                if conf_id in selected_ids:
                    has_conflict = True
                    break
            
            if has_conflict:
                rejected_playbooks.append({
                    "id": pb.id,
                    "name": pb.name,
                    "score": score,
                    "reason": "Conflict detected with active execution chain"
                })
                continue

            # Deduplication by category/findings overlap
            overlapping = False
            for active_item in selected_candidates:
                active_pb = active_item["playbook"]
                if active_pb.category == pb.category:
                    overlapping = True
                    break

            if overlapping:
                rejected_playbooks.append({
                    "id": pb.id,
                    "name": pb.name,
                    "score": score,
                    "reason": f"Deduplicated - category '{pb.category}' already covered by higher-priority playbook"
                })
                continue

            selected_candidates.append(item)
            selected_ids.add(pb.id)

        # Expand dependencies transitively for selected set
        final_playbooks = {item["playbook"].id: item["playbook"] for item in selected_candidates}
        stack = list(final_playbooks.values())
        while stack:
            pb = stack.pop()
            dep_ids = set(pb.dependencies) | set(pb.prerequisites)
            for dep_id in dep_ids:
                dep_pb = playbook_lookup.get(dep_id)
                if dep_pb and dep_pb.id not in final_playbooks:
                    # Score the dependency playbook
                    dep_score_data = self.score_playbook(dep_pb, current_urs, max_severity)
                    # Insert at the end as candidates
                    selected_candidates.append({
                        "playbook": dep_pb,
                        "score_data": dep_score_data
                    })
                    final_playbooks[dep_pb.id] = dep_pb
                    stack.append(dep_pb)

        # Deduplicate final set once more
        unique_selected = []
        seen_ids = set()
        for item in selected_candidates:
            if item["playbook"].id not in seen_ids:
                unique_selected.append(item)
                seen_ids.add(item["playbook"].id)

        # 5. Topological Sort Layer Ordering
        adj: Dict[str, Set[str]] = {item["playbook"].id: set() for item in unique_selected}
        indegree: Dict[str, int] = {item["playbook"].id: 0 for item in unique_selected}
        items_by_id = {item["playbook"].id: item for item in unique_selected}

        for item in unique_selected:
            pb = item["playbook"]
            deps = set(pb.dependencies) | set(pb.prerequisites)
            for d in deps:
                if d in adj:
                    adj[d].add(pb.id)
                    indegree[pb.id] += 1

        # Kahn's algorithm
        layers: List[List[Dict[str, Any]]] = []
        while True:
            zero_items = [items_by_id[n] for n, deg in indegree.items() if deg == 0]
            if not zero_items:
                break
            zero_items.sort(key=lambda x: x["score_data"]["priorityScore"], reverse=True)
            layers.append(zero_items)
            for item in zero_items:
                node_id = item["playbook"].id
                for succ in adj[node_id]:
                    indegree[succ] -= 1
                indegree[node_id] = -1

        # Flatten layers to ordered execution plan list
        ordered_items = list(itertools.chain.from_iterable(layers))

        # 6. Calculate Metrics
        playbooks_selected = len(ordered_items)
        playbooks_removed = playbooks_considered - playbooks_selected
        
        total_duration = sum(item["playbook"].estimated_execution_time for item in ordered_items)
        total_reduction = sum(item["playbook"].urs_reduction for item in ordered_items)
        total_disruption = sum(item["playbook"].disruption_score for item in ordered_items)
        total_recovery = sum(item["playbook"].recovery_score for item in ordered_items)

        opt_gain = round((total_reduction * 1.5) - (total_disruption * 1.0), 2)
        time_saved = round(sum(pb.estimated_execution_time for pb in compatible if pb.id not in seen_ids), 2)
        service_availability = max(0.0, round(100.0 - (total_disruption * 5.0), 2))
        expected_recovery = min(100.0, round(total_recovery * 10.0, 2))

        # Project URS reductions per step
        urs_steps = [current_urs]
        current_urs_projection = current_urs
        for layer in layers:
            layer_reduction = sum(item["playbook"].urs_reduction for item in layer)
            current_urs_projection = max(0.0, current_urs_projection - layer_reduction)
            urs_steps.append(round(current_urs_projection, 2))

        # Compile final timeline steps
        execution_order = []
        for idx, item in enumerate(ordered_items):
            pb = item["playbook"]
            score_data = item["score_data"]
            parallel = any(pb in [x["playbook"] for x in layer] for layer in layers if len(layer) > 1)
            
            execution_order.append({
                "step": idx + 1,
                "playbookId": pb.id,
                "title": pb.name,
                "category": pb.category,
                "priorityScore": score_data["priorityScore"],
                "selectedBecause": score_data["selectedBecause"],
                "scoreBreakdown": score_data["scoreBreakdown"],
                "dependencies": list(set(pb.dependencies) | set(pb.prerequisites)),
                "estimatedDuration": pb.estimated_execution_time,
                "ursReduction": pb.urs_reduction,
                "recoveryScore": pb.recovery_score,
                "disruptionScore": pb.disruption_score,
                "rollbackAvailable": bool(pb.rollback) or pb.rollback_supported,
                "parallel": parallel
            })

        dep_graph = {item["playbook"].id: list(set(item["playbook"].dependencies) | set(item["playbook"].prerequisites)) for item in ordered_items}
        opt_explanation = f"Selected {playbooks_selected} playbook(s) to secure baseline services, mitigating {max_severity} threat severity findings. Deduplicated {playbooks_removed} redundant playbooks to prevent service disruption."

        return {
            "incidentId": "INC-OPT-" + str(uuid.uuid4())[:8].upper(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "findings": findings,
            "optimizerMetadata": self.metadata,
            "metrics": {
                "optimizationGain": opt_gain,
                "playbooksConsidered": playbooks_considered,
                "playbooksSelected": playbooks_selected,
                "playbooksRemoved": playbooks_removed,
                "estimatedTimeSaved": time_saved,
                "estimatedRiskReduction": total_reduction,
                "estimatedServiceAvailability": service_availability,
                "expectedRecoveryPercentage": expected_recovery
            },
            "executionOrder": execution_order,
            "rejectedPlaybooks": rejected_playbooks,
            "ursBefore": current_urs,
            "ursAfter": urs_steps[-1],
            "ursProjection": urs_steps,
            "totalEstimatedDuration": total_duration,
            "overallConfidence": sum(item["playbook"].confidence for item in ordered_items) / max(1, playbooks_selected),
            "dependencyGraph": dep_graph,
            "optimizationRationale": opt_explanation,
            "conflictResolutionExplanation": f"Successfully filtered mutual exclusions. Active execution chain contains no overlapping components."
        }
