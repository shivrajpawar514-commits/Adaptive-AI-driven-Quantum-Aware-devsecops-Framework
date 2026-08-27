import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app, aws_provider, db_helper

client = TestClient(app)

MOCK_CLOUDWATCH_CPU_RESPONSE = {
    "Datapoints": [
        {
            "Timestamp": datetime.datetime(2026, 7, 20, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "Average": 18.5
        }
    ]
}

MOCK_CLOUDWATCH_SUM_RESPONSE = {
    "Datapoints": [
        {
            "Timestamp": datetime.datetime(2026, 7, 20, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "Sum": 65400.0
        }
    ]
}

@patch("boto3.client")
def test_cloudwatch_metrics_retrieval_mocked(mock_boto_client):
    mock_cw = MagicMock()
    
    def side_effect_stat(Namespace, MetricName, Dimensions, StartTime, EndTime, Period, Statistics):
        if MetricName == "CPUUtilization":
            return MOCK_CLOUDWATCH_CPU_RESPONSE
        return MOCK_CLOUDWATCH_SUM_RESPONSE

    mock_cw.get_metric_statistics.side_effect = side_effect_stat
    aws_provider._cw_client = mock_cw

    metrics = aws_provider.get_cloudwatch_metrics("i-04ba6569c74d41d59")
    
    assert metrics["instanceId"] == "i-04ba6569c74d41d59"
    assert metrics["cpu_usage"] == 18.5
    assert metrics["network_in"] == 65400
    assert metrics["mode"] == "LIVE"
    assert metrics["provider"] == "aws"

@patch("boto3.client")
def test_cloudwatch_missing_datapoints_fallback(mock_boto_client):
    mock_cw = MagicMock()
    mock_cw.get_metric_statistics.return_value = {"Datapoints": []}
    aws_provider._cw_client = mock_cw

    metrics = aws_provider.get_cloudwatch_metrics("i-04ba6569c74d41d59")
    assert metrics["mode"] == "SIMULATION MODE"
    assert metrics["cpu_usage"] == 15.2
    assert metrics["network_in"] == 58230

@patch("boto3.client")
def test_cloudwatch_unreachable_exception_fallback(mock_boto_client):
    mock_cw = MagicMock()
    mock_cw.get_metric_statistics.side_effect = Exception("AWS CloudWatch Unreachable")
    aws_provider._cw_client = mock_cw

    metrics = aws_provider.get_cloudwatch_metrics("i-04ba6569c74d41d59")
    assert metrics["mode"] == "SIMULATION MODE"
    assert metrics["cpu_usage"] == 15.2

@patch("boto3.client")
def test_cloudwatch_api_endpoint_instance(mock_boto_client):
    res = client.get("/cloud/aws/metrics/i-04ba6569c74d41d59")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["instanceId"] == "i-04ba6569c74d41d59"

@patch("boto3.client")
def test_cloudwatch_api_endpoint_live(mock_boto_client):
    mock_ec2 = MagicMock()
    mock_ec2.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-04ba6569c74d41d59",
                        "InstanceType": "t3.micro",
                        "State": {"Name": "running"},
                        "Tags": [{"Key": "Name", "Value": "server1"}]
                    }
                ]
            }
        ]
    }
    aws_provider._ec2_client = mock_ec2
    
    res = client.get("/cloud/aws/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["instances"]) == 1
    assert data["instances"][0]["instance"]["instanceId"] == "i-04ba6569c74d41d59"

def test_cloudwatch_mongodb_persistence():
    db_helper.save_metric({
        "instanceId": "i-04ba6569c74d41d59",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cpu_usage": 15.2,
        "mode": "LIVE"
    })
    if db_helper.is_mock:
        assert len(db_helper.mock_db["cloud_metrics"]) > 0
