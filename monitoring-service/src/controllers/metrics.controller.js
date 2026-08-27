const collectorService = require('../services/collector.service');
const prometheus = require('../config/prometheus');

class MetricsController {
  async getPrometheusMetrics(req, res, next) {
    try {
      res.set('Content-Type', prometheus.register.contentType);
      const metrics = await prometheus.register.metrics();
      res.end(metrics);
    } catch (err) {
      next(err);
    }
  }

  async getLatestMetrics(req, res, next) {
    try {
      const { instanceId } = req.query;
      const metrics = await collectorService.collectAll(instanceId);
      const cleanMetrics = JSON.parse(JSON.stringify(metrics));
      if (cleanMetrics.system && cleanMetrics.system.platform && !instanceId) {
        const parts = cleanMetrics.system.platform.split('|');
        cleanMetrics.system.platform = parts[0] || cleanMetrics.system.platform;
      }
      res.status(200).json({ status: 'success', data: cleanMetrics });
    } catch (err) {
      next(err);
    }
  }

  async getMetricsHistory(req, res, next) {
    try {
      const { instanceId } = req.query;
      const history = await collectorService.getHistory(instanceId);
      res.status(200).json({ status: 'success', data: history });
    } catch (err) {
      next(err);
    }
  }

  async getCpuMetrics(req, res, next) {
    try {
      const metrics = await collectorService.collectAll();
      res.status(200).json({ status: 'success', data: metrics.cpu });
    } catch (err) {
      next(err);
    }
  }

  async getMemoryMetrics(req, res, next) {
    try {
      const metrics = await collectorService.collectAll();
      res.status(200).json({ status: 'success', data: metrics.memory });
    } catch (err) {
      next(err);
    }
  }

  async getDiskMetrics(req, res, next) {
    try {
      const metrics = await collectorService.collectAll();
      res.status(200).json({ status: 'success', data: metrics.disk });
    } catch (err) {
      next(err);
    }
  }

  async getNetworkMetrics(req, res, next) {
    try {
      const metrics = await collectorService.collectAll();
      res.status(200).json({ status: 'success', data: metrics.network });
    } catch (err) {
      next(err);
    }
  }

  async getSystemMetrics(req, res, next) {
    try {
      const metrics = await collectorService.collectAll();
      res.status(200).json({ status: 'success', data: metrics.system });
    } catch (err) {
      next(err);
    }
  }

  async updateLatencies(req, res, next) {
    try {
      prometheus.updateLatencies(req.body);
      res.status(200).json({ status: 'success', message: 'Metrics updated successfully' });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new MetricsController();
