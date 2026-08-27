const client = require('prom-client');

const collectDefaultMetrics = client.collectDefaultMetrics;
const Registry = client.Registry;
const register = new Registry();

collectDefaultMetrics({ register });

const cpuGauge = new client.Gauge({
  name: 'system_cpu_utilization_ratio',
  help: 'System CPU utilization ratio',
  registers: [register]
});

const memoryGauge = new client.Gauge({
  name: 'system_memory_utilization_ratio',
  help: 'System memory utilization ratio',
  registers: [register]
});

const diskGauge = new client.Gauge({
  name: 'system_disk_utilization_ratio',
  help: 'System disk utilization ratio',
  registers: [register]
});

const netRxGauge = new client.Gauge({
  name: 'system_network_bytes_rx_total',
  help: 'Total network bytes received',
  registers: [register]
});

const netTxGauge = new client.Gauge({
  name: 'system_network_bytes_tx_total',
  help: 'Total network bytes transmitted',
  registers: [register]
});

// Sprint 27.3 Latency & Operational Metrics
const apiAvgLatencyGauge = new client.Gauge({
  name: 'api_average_latency_ms',
  help: 'Average REST API response latency in milliseconds',
  registers: [register]
});

const predictionLatencyGauge = new client.Gauge({
  name: 'prediction_latency_ms',
  help: 'Prediction Engine forecast response latency in milliseconds',
  registers: [register]
});

const riskLatencyGauge = new client.Gauge({
  name: 'risk_engine_latency_ms',
  help: 'Risk Engine URS calculation response latency in milliseconds',
  registers: [register]
});

const automationLatencyGauge = new client.Gauge({
  name: 'automation_latency_ms',
  help: 'Automation Engine playbook generation response latency in milliseconds',
  registers: [register]
});

const policyLatencyGauge = new client.Gauge({
  name: 'policy_latency_ms',
  help: 'Policy Engine rule recommendations response latency in milliseconds',
  registers: [register]
});

const pipelineLatencyGauge = new client.Gauge({
  name: 'pipeline_latency_ms',
  help: 'Orchestration pipeline execution latency in milliseconds',
  registers: [register]
});

const successRateGauge = new client.Gauge({
  name: 'pipeline_success_rate',
  help: 'Percentage of successful pipeline runs',
  registers: [register]
});

const failureRateGauge = new client.Gauge({
  name: 'pipeline_failure_rate',
  help: 'Percentage of failed pipeline runs',
  registers: [register]
});

const updatePrometheusMetrics = (data) => {
  cpuGauge.set(data.cpu.utilization / 100);
  memoryGauge.set(data.memory.usagePercent / 100);
  diskGauge.set(data.disk.usagePercent / 100);
  netRxGauge.set(data.network.bytesRx);
  netTxGauge.set(data.network.bytesTx);
};

const updateLatencies = (data) => {
  if (data.apiAvgLatency !== undefined) apiAvgLatencyGauge.set(data.apiAvgLatency);
  if (data.predictionLatency !== undefined) predictionLatencyGauge.set(data.predictionLatency);
  if (data.riskLatency !== undefined) riskLatencyGauge.set(data.riskLatency);
  if (data.automationLatency !== undefined) automationLatencyGauge.set(data.automationLatency);
  if (data.policyLatency !== undefined) policyLatencyGauge.set(data.policyLatency);
  if (data.pipelineLatency !== undefined) pipelineLatencyGauge.set(data.pipelineLatency);
  if (data.successRate !== undefined) successRateGauge.set(data.successRate);
  if (data.failureRate !== undefined) failureRateGauge.set(data.failureRate);
};

module.exports = {
  register,
  updatePrometheusMetrics,
  updateLatencies
};
