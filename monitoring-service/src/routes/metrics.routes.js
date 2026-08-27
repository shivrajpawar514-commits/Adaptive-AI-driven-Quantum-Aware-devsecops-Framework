const express = require('express');
const router = express.Router();
const metricsController = require('../controllers/metrics.controller');

/**
 * @openapi
 * /metrics:
 *   get:
 *     summary: Prometheus scrapable metrics output
 *     responses:
 *       200:
 *         description: Prometheus formatted text metrics
 */
router.get('/metrics', metricsController.getPrometheusMetrics);

/**
 * @openapi
 * /api/metrics:
 *   get:
 *     summary: Full JSON representation of system metrics
 *     responses:
 *       200:
 *         description: JSON formatted telemetry details
 */
router.get('/api/metrics', metricsController.getLatestMetrics);

/**
 * @openapi
 * /api/metrics/history:
 *   get:
 *     summary: Rich history of rolling system telemetry metrics (up to 300 samples)
 *     responses:
 *       200:
 *         description: JSON formatted array of telemetry history samples with metadata
 */
router.get('/api/metrics/history', metricsController.getMetricsHistory);

/**
 * @openapi
 * /metrics/cpu:
 *   get:
 *     summary: CPU specific metrics
 *     responses:
 *       200:
 *         description: JSON formatted CPU metrics
 */
router.get('/metrics/cpu', metricsController.getCpuMetrics);

/**
 * @openapi
 * /metrics/memory:
 *   get:
 *     summary: Memory specific metrics
 *     responses:
 *       200:
 *         description: JSON formatted memory metrics
 */
router.get('/metrics/memory', metricsController.getMemoryMetrics);

/**
 * @openapi
 * /metrics/disk:
 *   get:
 *     summary: Disk mount statistics
 *     responses:
 *       200:
 *         description: JSON formatted disk metrics
 */
router.get('/metrics/disk', metricsController.getDiskMetrics);

/**
 * @openapi
 * /metrics/network:
 *   get:
 *     summary: Primary network interface metrics
 *     responses:
 *       200:
 *         description: JSON formatted network metrics
 */
router.get('/metrics/network', metricsController.getNetworkMetrics);

/**
 * @openapi
 * /metrics/system:
 *   get:
 *     summary: Basic host parameters
 *     responses:
 *       200:
 *         description: JSON formatted host metrics
 */
router.get('/metrics/system', metricsController.getSystemMetrics);

/**
 * @openapi
 * /api/metrics/update_latencies:
 *   post:
 *     summary: Update Prometheus gauges with measured system and pipeline latency metrics
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *     responses:
 *       200:
 *         description: Latency metrics updated successfully
 */
router.post('/api/metrics/update_latencies', metricsController.updateLatencies);

module.exports = router;
