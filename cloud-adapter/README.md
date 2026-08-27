# Cloud Adapter Microservice

The **Cloud Adapter Microservice** connects the DevSecOps framework to cloud providers (AWS) using `boto3`. It dynamically discovers cloud assets (EC2 instances), queries CloudWatch telemetry metrics, assesses cryptographic and security group posture, and persists real-time asset data into MongoDB.

---

## 1. Prerequisites & AWS Configuration

### AWS CLI & Boto3 Setup
Ensure AWS CLI is installed and configured on your host machine or container environment:

```bash
aws configure
```

Alternatively, export AWS credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
```

---

## 2. Required IAM Permissions

The AWS IAM policy attached to the user/role running this microservice requires the following minimum permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DevSecOpsCloudAdapterPermissions",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeSecurityGroups",
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 3. Environment Variables

| Variable Name | Description | Default Value | Required |
| :--- | :--- | :--- | :--- |
| `AWS_REGION` | AWS Region target for EC2 discovery & CloudWatch | `us-east-1` | No |
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | Inherited from AWS CLI / IAM Role | Conditional |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | Inherited from AWS CLI / IAM Role | Conditional |
| `AWS_SESSION_TOKEN` | AWS Session Token (for STS / temporary credentials) | None | No |
| `MONGO_URI` | Connection URI for MongoDB storage | `mongodb://localhost:27017` | Recommended |
| `PORT` | Microservice execution HTTP port | `7000` | No |

---

## 4. API Endpoints Matrix

- **`GET /cloud/assets`**: Dynamically fetches live EC2 inventory via boto3, stores inventory into MongoDB collection `cloud_assets`, and returns current inventory list. Raises HTTP 502 if AWS is unreachable.
- **`GET /cloud/aws/discover`**: Explicitly triggers fresh EC2 discovery across configured region.
- **`GET /cloud/aws/metrics?instanceId={id}`**: Queries CloudWatch telemetry metrics for specific EC2 instance.
- **`GET /cloud/security-posture?instanceId={id}`**: Scans security group rules (wildcard SSH/RDP ingress) and resource tags.
- **`POST /cloud/aws/register`**: Registers an EC2 instance ID as the primary monitoring target for pipeline ingestion.

---

## 5. Local Execution & Testing

### Running the Microservice Locally
```bash
cd cloud-adapter
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 7000
```

### Running Unit Tests (Mocked AWS boto3)
```bash
pytest tests/
```

---

## 6. Docker Deployment

Docker deployment automatically passes through local or environment-level AWS credentials:

```bash
docker build -t cloud-adapter .
docker run -d -p 7000:7000 \
  -e AWS_REGION="us-east-1" \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e MONGO_URI="mongodb://mongo:27017" \
  cloud-adapter
```

---

## 7. Live CloudWatch Monitoring Pipeline

### Architecture Overview
```
EC2 Instance -> CloudWatch -> Cloud Adapter (port 7000) -> MongoDB (cloud_metrics) -> Monitoring Service (port 6001) -> AI Engine (port 8000) -> Risk Engine (port 8500) -> QRAE -> Policy Engine (port 8800) -> Research Evaluator (port 8900) -> Report Generator (port 9000) -> Frontend Dashboard (port 5173)
```

### Scraped CloudWatch Metrics
| Metric Name | Unit | Collection Stat | Description |
| :--- | :--- | :--- | :--- |
| `CPUUtilization` | Percent | Average | Percentage of allocated EC2 compute units currently in use |
| `NetworkIn` | Bytes | Sum | Total bytes received across all network interfaces |
| `NetworkOut` | Bytes | Sum | Total bytes sent across all network interfaces |
| `DiskReadOps` | Count | Sum | Completed I/O read operations to ephemeral/EBS storage |
| `DiskWriteOps` | Count | Sum | Completed I/O write operations to ephemeral/EBS storage |
| `StatusCheckFailed` | Count | Sum | Combined system and instance status check failure status |

### MongoDB Schema (`cloud_metrics` collection)
```json
{
  "instanceId": "i-04ba6569c74d41d59",
  "timestamp": "2026-07-20T12:00:00Z",
  "cpu_usage": 15.2,
  "network_in": 58230,
  "network_out": 43812,
  "disk_read_ops": 7,
  "disk_write_ops": 9,
  "status_failed": 0,
  "provider": "aws",
  "region": "us-east-1",
  "mode": "LIVE"
}
```

### Simulation Fallback Strategy
When AWS credentials are missing, or CloudWatch returns no datapoints, the Cloud Adapter automatically switches to `SIMULATION MODE`. Normalized telemetry matching the standard pipeline schema is emitted seamlessly without crashing any downstream microservice.
