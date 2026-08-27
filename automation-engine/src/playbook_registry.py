# Playbook Registry for Adaptive SOAR Decision Engine

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Playbook:
    """Metadata definition for a remediation playbook.

    All fields are optional where appropriate; the engine uses the defined
    attributes to match, rank and execute a playbook.
    """
    id: str
    name: str
    description: str
    # Findings this playbook can address – list of keywords/patterns (case‑insensitive substring match)
    supported_findings: List[str] = field(default_factory=list)
    # AWS resources (e.g., "ec2", "security_group", "waf") the playbook works against
    supported_resources: List[str] = field(default_factory=list)
    severity: List[str] = field(default_factory=list)  # e.g. ["critical", "high"]
    urs_reduction: float = 0.0  # Expected URS reduction points
    confidence: float = 0.5  # AI confidence (0‑1)
    dependencies: List[str] = field(default_factory=list)  # IDs of playbooks that should run before this one
    rollback: Optional[str] = None  # Command or script to rollback the change
    verification: Optional[str] = None  # Command or script to verify remediation
    aws_sdk_function: Optional[str] = None  # Name of a boto3 helper function (placeholder)
    aws_cli_command: Optional[str] = None
    terraform_snippet: Optional[str] = None
    cloudformation_snippet: Optional[str] = None
    estimated_execution_time: float = 0.0  # seconds
    estimated_downtime: float = 0.0  # seconds
    mitre_mapping: List[str] = field(default_factory=list)
    business_impact: float = 0.0  # 0‑1 weighting for ranking
    # Extended metadata for chaining and execution
    prerequisites: List[str] = field(default_factory=list)  # playbook IDs that must be completed before this one
    conflicts: List[str] = field(default_factory=list)      # playbook IDs that cannot coexist in the same chain
    execution_order: Optional[int] = None                 # explicit order hint (lower runs earlier)
    can_run_in_parallel: bool = True                     # if True, may be scheduled with other independent playbooks
    required_aws_service: List[str] = field(default_factory=list)  # e.g., ["ec2", "waf"]
    required_permissions: List[str] = field(default_factory=list) # e.g., ["ec2:StopInstances"]
    historical_success_rate: float = 0.5  # placeholder for future stats
    
    # Enrichments for Sprint 28 Playbook Optimization
    category: str = "General"
    compatible_cloud: str = "aws"
    rollback_supported: bool = False
    recovery_score: float = 5.0
    disruption_score: float = 5.0
    execution_priority: str = "Medium"
    mitigation_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation used by the API response."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "supportedFindings": self.supported_findings,
            "supportedResources": self.supported_resources,
            "severity": self.severity,
            "ursReduction": self.urs_reduction,
            "confidence": self.confidence,
            "dependencies": self.dependencies,
            "rollbackAvailable": bool(self.rollback) or self.rollback_supported,
            "verificationAvailable": bool(self.verification),
            "awsCliCommand": self.aws_cli_command,
            "terraformSnippet": self.terraform_snippet,
            "cloudformationSnippet": self.cloudformation_snippet,
            "estimatedExecutionTime": self.estimated_execution_time,
            "estimatedDowntime": self.estimated_downtime,
            "mitreMapping": self.mitre_mapping,
            "category": self.category,
            "compatibleCloud": self.compatible_cloud,
            "rollbackSupported": bool(self.rollback) or self.rollback_supported,
            "recoveryScore": self.recovery_score,
            "disruptionScore": self.disruption_score,
            "executionPriority": self.execution_priority,
            "mitigationTags": self.mitigation_tags,
            "businessImpact": self.business_impact,
        }

    def decision_reasoning(self) -> str:
        """Generate a simple human‑readable explanation for why this playbook was chosen.
        In a real system this would be powered by an XAI model; here we compose a string.
        """
        parts = []
        if self.severity:
            parts.append(f"addresses {', '.join(self.severity)} severity findings")
        if self.urs_reduction:
            parts.append(f"expected URS reduction of {self.urs_reduction} points")
        if self.business_impact:
            parts.append(f"low business impact ({self.business_impact:.2f})")
        if self.estimated_downtime:
            parts.append(f"downtime ~{self.estimated_downtime}s")
        return "; ".join(parts) if parts else "No specific reasoning available"

# ---------------------------------------------------------------------------
# Registry definition – add new playbooks here without touching the engine.
# ---------------------------------------------------------------------------

PLAYBOOKS_REGISTRY: List[Playbook] = [
    Playbook(
        id="isolate_ec2",
        name="Isolate Compromised EC2 Instance",
        description="Gracefully stops the target EC2 instance to prevent lateral movement.",
        supported_findings=["crypto", "malware", "compromise", "isolate"],
        supported_resources=["ec2"],
        severity=["critical", "high"],
        urs_reduction=15.0,
        confidence=0.9,
        dependencies=[],
        rollback="aws ec2 start-instances --instance-ids {instance_id}",
        verification="aws ec2 describe-instance-status --instance-ids {instance_id}",
        aws_cli_command="aws ec2 stop-instances --instance-ids {instance_id} --region us-east-1",
        estimated_execution_time=8.0,
        estimated_downtime=30.0,
        mitre_mapping=["T1489"],
        business_impact=0.8,
        category="Isolation",
        compatible_cloud="aws",
        rollback_supported=True,
        recovery_score=8.5,
        disruption_score=7.0,
        execution_priority="High",
        mitigation_tags=["network", "containment"],
    ),
    Playbook(
        id="scale_ec2",
        name="Scale EC2 Instance Type",
        description="Upgrade instance type to mitigate CPU / memory pressure.",
        supported_findings=["cpu", "high cpu", "resource exhaustion"],
        supported_resources=["ec2"],
        severity=["high", "medium"],
        urs_reduction=8.0,
        confidence=0.85,
        dependencies=[],
        rollback="aws ec2 modify-instance-attribute --instance-id {instance_id} --instance-type '{{\"Value\": \"t2.micro\"}}'",
        verification="aws ec2 describe-instances --instance-ids {instance_id}",
        aws_cli_command="aws ec2 modify-instance-attribute --instance-id {instance_id} --instance-type '{{\"Value\": \"t3.medium\"}}'",
        estimated_execution_time=5.0,
        estimated_downtime=10.0,
        mitre_mapping=["T1499"],
        business_impact=0.4,
        category="Configuration",
        compatible_cloud="aws",
        rollback_supported=True,
        recovery_score=6.0,
        disruption_score=3.0,
        execution_priority="Medium",
        mitigation_tags=["capacity", "performance"],
    ),
    Playbook(
        id="restrict_ssh_sg",
        name="Restrict Wildcard SSH Security Group Rule",
        description="Remove 0.0.0.0/0 SSH ingress from the security group.",
        supported_findings=["ssh open", "wildcard sg", "port 22"],
        supported_resources=["security_group"],
        severity=["high", "medium"],
        urs_reduction=10.0,
        confidence=0.92,
        dependencies=[],
        rollback="aws ec2 authorize-security-group-ingress --group-id {sg_id} --protocol tcp --port 22 --cidr 0.0.0.0/0",
        verification="aws ec2 describe-security-groups --group-ids {sg_id}",
        aws_cli_command="aws ec2 revoke-security-group-ingress --group-id {sg_id} --protocol tcp --port 22 --cidr 0.0.0.0/0",
        estimated_execution_time=3.0,
        estimated_downtime=0.0,
        mitre_mapping=["T1046"],
        business_impact=0.2,
        category="Access Control",
        compatible_cloud="aws",
        rollback_supported=True,
        recovery_score=9.0,
        disruption_score=1.0,
        execution_priority="Critical",
        mitigation_tags=["firewall", "network-security"],
    ),
    Playbook(
        id="attach_waf",
        name="Attach AWS WAF Rate Limiting ACL",
        description="Apply a WAF ACL to protect API endpoints from volumetric attacks.",
        supported_findings=["ddos", "rate limit", "network flood"],
        supported_resources=["waf", "api_gateway"],
        severity=["high"],
        urs_reduction=12.0,
        confidence=0.88,
        dependencies=[],
        rollback="aws wafv2 delete-web-acl --arn {web_acl_arn}",
        verification="aws wafv2 get-web-acl --arn {web_acl_arn}",
        aws_cli_command="aws wafv2 associate-web-acl --web-acl-arn {web_acl_arn} --resource-arn {resource_arn}",
        estimated_execution_time=6.0,
        estimated_downtime=5.0,
        mitre_mapping=["T1498"],
        business_impact=0.3,
        category="Access Control",
        compatible_cloud="aws",
        rollback_supported=True,
        recovery_score=7.5,
        disruption_score=2.0,
        execution_priority="High",
        mitigation_tags=["waf", "ddos-protection"],
    ),
    # Additional playbooks can be added here following the same pattern.
]

# Helper to retrieve a playbook by ID
def get_playbook_by_id(playbook_id: str) -> Optional[Playbook]:
    for pb in PLAYBOOKS_REGISTRY:
        if pb.id == playbook_id:
            return pb
    return None
