from fastapi.testclient import TestClient
from src.main import app, compile_metrics_math, generate_report_text, format_markdown_report, format_csv_metrics

client = TestClient(app)

def test_metrics_calculations():
    metrics = compile_metrics_math()
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1Score" in metrics
    assert "detectionLatencyMs" in metrics
    
    # Assert math bounds
    assert 0.0 <= metrics["accuracy"] <= 100.0
    assert 0.0 <= metrics["precision"] <= 100.0
    assert 0.0 <= metrics["recall"] <= 100.0
    assert 0.0 <= metrics["f1Score"] <= 100.0

def test_report_text_generation():
    metrics = compile_metrics_math()
    sections = generate_report_text(metrics)
    assert "Executive Summary" in sections
    assert "Experimental Methodology" in sections
    assert "Discussion" in sections
    
    # Check interpolation success
    assert f"{metrics['accuracy']}%" in sections["Executive Summary"]
    assert f"{metrics['precision']}%" in sections["Executive Summary"]

def test_exporters():
    metrics = compile_metrics_math()
    sections = generate_report_text(metrics)
    
    # Markdown exporter
    md = format_markdown_report(metrics, sections)
    assert "# Publication Research Report" in md
    assert "## 1. Executive Summary" in md
    assert "## 3. Benchmark Comparison Results" in md
    assert f"{metrics['accuracy']}%" in md
    
    # CSV exporter
    csv_str = format_csv_metrics(metrics)
    assert "Metric Name,Value" in csv_str
    assert "F1 Score" in csv_str

def test_api_endpoints():
    # POST generate
    res_post = client.post("/report/generate")
    assert res_post.status_code == 200
    assert res_post.json()["status"] == "success"
    
    # GET latest
    res_lat = client.get("/report/latest")
    assert res_lat.status_code == 200
    latest_data = res_lat.json()["data"]
    assert "reportId" in latest_data
    assert "markdown" in latest_data
    assert "csv" in latest_data
    
    # GET history
    res_hist = client.get("/report/history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()["data"]) >= 1
