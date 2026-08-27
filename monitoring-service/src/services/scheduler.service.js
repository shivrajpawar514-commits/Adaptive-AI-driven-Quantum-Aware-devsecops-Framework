const collectorService = require('./collector.service');
const MonitoringMetric = require('../models/metric.model');
const prometheus = require('../config/prometheus');
const logger = require('../config/logger');

class SchedulerService {
  constructor() {
    this.intervalId = null;
  }

  start(intervalMs = 10000) {
    logger.info(`Starting metrics collection scheduler (every ${intervalMs / 1000}s)`);
    this.runJob();
    this.intervalId = setInterval(() => this.runJob(), intervalMs);
  }

  async runJob() {
    try {
      const data = await collectorService.collectAll();
      prometheus.updatePrometheusMetrics(data);
      const metricDoc = new MonitoringMetric(data);
      await metricDoc.save();
      logger.info('System telemetry collected and saved successfully');
    } catch (err) {
      logger.error('Telemetry collection job failed:', err.message);
    }
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      logger.info('Metrics collection scheduler stopped.');
    }
  }
}

module.exports = new SchedulerService();
