import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from botocore.exceptions import ClientError
from src.main import app, aws_provider

client = TestClient(app)

MOCK_DESCRIBE_INSTANCES_RESPONSE = {
    "Reservations": [
        {
            "ReservationId": "r-1234567890abcdef0",
            "Instances": [
                {
                    "InstanceId": "i-04ba6569c74d41d59",
                    "InstanceType": "t3.micro",
                    "State": {"Code": 16, "Name": "running"},
                    "PublicIpAddress": "54.208.119.29",
                    "PrivateIpAddress": "172.31.21.216",
                    "Placement": {"AvailabilityZone": "us-east-1c"},
                    "VpcId": "vpc-07b25889789f9fc21",
                    "SubnetId": "subnet-08b10c670133472f3",
                    "ImageId": "ami-00adafae70b8029d8",
                    "PlatformDetails": "Red Hat Enterprise Linux",
                    "LaunchTime": datetime.datetime(2026, 7, 19, 12, 49, 54, tzinfo=datetime.timezone.utc),
                    "SecurityGroups": [{"GroupId": "sg-0e6ff0385dc3e9235", "GroupName": "launch-wizard-15"}],
                    "Tags": [{"Key": "Name", "Value": "server1"}, {"Key": "Environment", "Value": "Production"}]
                }
            ]
        }
    ]
}

def test_providers_endpoint():
    res = client.get("/cloud/providers")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["providers"]) == 3
    assert data["providers"][0]["name"] == "aws"

@patch("boto3.client")
def test_aws_adapter_ec2_discovery_mocked(mock_boto_client):
    mock_ec2 = MagicMock()
    mock_ec2.describe_instances.return_value = MOCK_DESCRIBE_INSTANCES_RESPONSE
    mock_boto_client.return_value = mock_ec2

    aws_provider._ec2_client = mock_ec2
    assets = aws_provider.discover_assets()

    assert len(assets) == 1
    inst = assets[0]
    assert inst["instanceId"] == "i-04ba6569c74d41d59"
    assert inst["instanceName"] == "server1"
    assert inst["instanceType"] == "t3.micro"
    assert inst["state"] == "running"
    assert inst["publicIp"] == "54.208.119.29"
    assert inst["privateIp"] == "172.31.21.216"
    assert inst["vpcId"] == "vpc-07b25889789f9fc21"
    assert inst["subnetId"] == "subnet-08b10c670133472f3"
    assert inst["ami"] == "ami-00adafae70b8029d8"
    assert inst["securityGroups"] == ["launch-wizard-15"]
    assert inst["platform"] == "Red Hat Enterprise Linux"
    assert inst["tags"]["Environment"] == "Production"

@patch("boto3.client")
def test_aws_adapter_zero_instances(mock_boto_client):
    mock_ec2 = MagicMock()
    mock_ec2.describe_instances.return_value = {"Reservations": []}
    aws_provider._ec2_client = mock_ec2

    assets = aws_provider.discover_assets()
    assert assets == []

@patch("boto3.client")
def test_aws_unreachable_returns_502(mock_boto_client):
    mock_ec2 = MagicMock()
    mock_ec2.describe_instances.side_effect = Exception("AWS Endpoint Unreachable")
    aws_provider._ec2_client = mock_ec2

    res = client.get("/cloud/assets")
    assert res.status_code == 502
    assert "Failed to fetch AWS assets" in res.json()["detail"]

def test_register_endpoint():
    payload = {"instanceId": "i-04ba6569c74d41d59"}
    res = client.post("/cloud/aws/register", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

