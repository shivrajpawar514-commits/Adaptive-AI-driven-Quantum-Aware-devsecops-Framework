from fastapi.testclient import TestClient
from src.main import app, db_helper

client = TestClient(app)

def test_topology_endpoint():
    res = client.get("/digital-twin/topology")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "layers" in data
    assert "relationships" in data
    
    layers = data["layers"]
    assert layers["provider"] == "aws"
    assert layers["vpc"] == "vpc-12345"

def test_assets_endpoints():
    # Sync mock data first
    res_sync = client.post("/digital-twin/sync")
    assert res_sync.status_code == 200
    
    # Get all assets
    res_assets = client.get("/digital-twin/assets")
    assert res_assets.status_code == 200
    assets = res_assets.json()["data"]
    assert len(assets) == 2
    assert assets[0]["assetId"] == "i-09f1a238b7e456cde"
    
    # Get single asset by ID
    res_single = client.get("/digital-twin/asset/i-09f1a238b7e456cde")
    assert res_single.status_code == 200
    single_data = res_single.json()["data"]
    assert single_data["instanceName"] == "production-web-node-01"
    
    # Get asset ID not found
    res_missing = client.get("/digital-twin/asset/i-missinginstance")
    assert res_missing.status_code == 404

def test_graph_visualization_json():
    # Sync
    client.post("/digital-twin/sync")
    
    # Get graph data
    res = client.get("/digital-twin/graph")
    assert res.status_code == 200
    graph_data = res.json()["data"]
    
    assert "nodes" in graph_data
    assert "edges" in graph_data
    
    # Check that AWS provider node, VPC node and EC2 nodes exist
    nodes = graph_data["nodes"]
    node_ids = [n["id"] for n in nodes]
    assert "aws" in node_ids
    assert "vpc-12345" in node_ids
    assert "i-09f1a238b7e456cde" in node_ids
    
    # Check node attributes
    aws_node = [n for n in nodes if n["id"] == "aws"][0]
    assert aws_node["type"] == "Provider"
    assert aws_node["icon"] == "cloud"
    
    ec2_node = [n for n in nodes if n["id"] == "i-09f1a238b7e456cde"][0]
    assert ec2_node["group"] == "Compute"
    assert ec2_node["riskColor"] in ("green", "yellow", "orange", "red")
