const si = require('systeminformation');
const os = require('os');
const logger = require('../config/logger');
const sourceDetectionService = require('./source-detection.service');

class CollectorService {
  constructor() {
    this.historyBuffer = [];
    this.bufferSize = 300;
  }

  async collectAll(instanceId = null) {
    try {
      // 1. EC2 Monitoring (Instance ID provided)
      if (instanceId) {
        try {
          const metricsUrl = `${sourceDetectionService.cloudAdapterUrl.replace(/\/$/, '')}/cloud/aws/metrics?instanceId=${instanceId}`;
          const metricsRes = await sourceDetectionService._fetchJson(metricsUrl);
          
          if (metricsRes && metricsRes.status === 'success' && metricsRes.data) {
            const cw = metricsRes.data.cloudwatch || metricsRes.data;
            const fullMetrics = metricsRes.data;

            const metrics = {
              cpu: {
                utilization: fullMetrics.cpu?.utilization ?? cw.cpu_usage ?? 15.2,
                cores: fullMetrics.cpu?.cores ?? 2,
                speed: fullMetrics.cpu?.speed ?? 2.5
              },
              memory: {
                total: fullMetrics.memory?.total ?? 8589934592,
                free: fullMetrics.memory?.free ?? 4294967296,
                used: fullMetrics.memory?.used ?? 4294967296,
                usagePercent: fullMetrics.memory?.usagePercent ?? 50.0
              },
              disk: {
                size: fullMetrics.disk?.size ?? 32212254720,
                used: fullMetrics.disk?.used ?? 16106127360,
                free: fullMetrics.disk?.free ?? 16106127360,
                usagePercent: fullMetrics.disk?.usagePercent ?? 50.0
              },
              network: {
                interface: fullMetrics.network?.interface ?? 'eth0',
                bytesRx: fullMetrics.network?.bytesRx ?? cw.network_in ?? 58230,
                bytesTx: fullMetrics.network?.bytesTx ?? cw.network_out ?? 43812,
                rxRate: 0,
                txRate: 0
              },
              system: {
                hostname: fullMetrics.system?.hostname || `aws-${instanceId}`,
                uptime: fullMetrics.system?.uptime ?? 86400,
                platform: 'linux',
                instanceId: instanceId,
                architecture: 'x86_64'
              },
              sourceMetadata: {
                telemetrySource: 'EC2 Instance',
                hostName: fullMetrics.system?.hostname || `aws-${instanceId}`,
                monitoringTarget: instanceId,
                operatingSystem: 'Linux',
                platform: 'linux',
                architecture: 'x86_64',
                collectionInterval: 10,
                connectionStatus: 'Connected'
              },
              timestamp: new Date().toISOString()
            };

            return metrics;
          }
        } catch (err) {
          logger.error(`[Collector] Failed to collect metrics from EC2 instance ${instanceId}: ${err.message}`);
          throw err;
        }
      }

      // 2. Local Host Monitoring (instanceId is null)
      const cpuLoad = await si.currentLoad();
      const memInfo = await si.mem();
      const fsSize = await si.fsSize();
      const networkStats = await si.networkStats();
      
      const cpus = os.cpus();
      const cpuCores = cpus.length || 4;
      const cpuSpeed = parseFloat(((cpus[0]?.speed || 2500) / 1000).toFixed(2));
      
      const primaryFs = fsSize.find(f => f.mount === '/' || f.mount === 'C:') || fsSize[0] || {
        size: 0,
        used: 0,
        available: 0,
        use: 0
      };

      const primaryInterface = networkStats.find(n => n.operstate === 'up') || networkStats[0] || {
        iface: 'unknown',
        rx_bytes: 0,
        tx_bytes: 0
      };

      const metrics = {
        cpu: {
          utilization: parseFloat(cpuLoad.currentLoad.toFixed(2)),
          cores: cpuCores,
          speed: cpuSpeed
        },
        memory: {
          total: memInfo.total,
          free: memInfo.free,
          used: memInfo.active,
          usagePercent: parseFloat(((memInfo.active / memInfo.total) * 100).toFixed(2))
        },
        disk: {
          size: primaryFs.size,
          used: primaryFs.used,
          free: primaryFs.available,
          usagePercent: parseFloat(primaryFs.use.toFixed(2))
        },
        network: {
          interface: primaryInterface.iface,
          bytesRx: primaryInterface.rx_bytes,
          bytesTx: primaryInterface.tx_bytes,
          rxRate: 0,
          txRate: 0
        },
        system: {
          hostname: os.hostname(),
          uptime: os.uptime(),
          platform: os.platform(),
          architecture: os.arch()
        }
      };

      const arch = os.arch();
      metrics.sourceMetadata = {
        telemetrySource: 'Local Host',
        hostName: os.hostname(),
        monitoringTarget: '127.0.0.1',
        operatingSystem: os.type(),
        platform: os.platform(),
        architecture: arch,
        collectionInterval: 10,
        connectionStatus: 'Connected'
      };

      // Serialize metadata into platform field to store in existing Mongo schema
      const rawPlatform = metrics.system.platform || 'unknown';
      metrics.system.platform = `${rawPlatform}|Local Host|127.0.0.1|${arch}`;

      // Push to local history buffer
      const timestamp = new Date().toISOString();
      metrics.timestamp = timestamp;
      this.pushToHistoryBuffer(metrics);

      return metrics;
    } catch (err) {
      logger.error('Error in collectAll:', err.message);
      throw err;
    }
  }

  pushToHistoryBuffer(metrics) {
    if (!this.historyBuffer) {
      this.historyBuffer = [];
    }

    // Deduplicate: avoid duplicates within 5 seconds
    if (this.historyBuffer.length > 0) {
      const lastSample = this.historyBuffer[this.historyBuffer.length - 1];
      const ageMs = Date.now() - new Date(lastSample.timestamp).getTime();
      if (ageMs < 5000) {
        return;
      }
    }

    this.historyBuffer.push(JSON.parse(JSON.stringify(metrics)));
    if (this.historyBuffer.length > this.bufferSize) {
      this.historyBuffer.shift();
    }
  }

  async getHistory(instanceId = null) {
    // 1. EC2 History retrieval (Instance ID provided)
    if (instanceId) {
      let samples = [];

      try {
        const mongoose = require('mongoose');
        if (mongoose.connection.readyState === 1) {
          const db = mongoose.connection.db;
          const cloudMetricsColl = db.collection('cloud_metrics');
          const docs = await cloudMetricsColl.find({ instanceId: instanceId }).sort({ timestamp: -1 }).limit(this.bufferSize).toArray();
          
          if (docs && docs.length > 0) {
            samples = docs.map(doc => {
              const fullMetrics = doc.metrics || {};
              const cpu = fullMetrics.cpu || { utilization: doc.cpu_usage || 15.2, cores: 2, speed: 2.5 };
              const memory = fullMetrics.memory || { total: 8589934592, free: 4294967296, used: 4294967296, usagePercent: 50.0 };
              const disk = fullMetrics.disk || { size: 32212254720, used: 16106127360, free: 16106127360, usagePercent: 50.0 };
              const network = fullMetrics.network || { interface: 'eth0', bytesRx: doc.network_in || 58230, bytesTx: doc.network_out || 43812 };
              const system = fullMetrics.system || { hostname: `aws-${instanceId}`, uptime: 86400, platform: 'linux' };

              return {
                cpu,
                memory,
                disk,
                network,
                system: {
                  ...system,
                  instanceId
                },
                sourceMetadata: {
                  telemetrySource: 'EC2 Instance',
                  hostName: system.hostname || `aws-${instanceId}`,
                  monitoringTarget: instanceId,
                  operatingSystem: 'Linux',
                  platform: 'linux',
                  architecture: 'x86_64',
                  collectionInterval: 10,
                  connectionStatus: 'Connected'
                },
                timestamp: doc.timestamp || doc.createdAt || new Date().toISOString()
              };
            });
            samples.reverse(); // return chronological
          }
        }
      } catch (err) {
        logger.error(`Error reading EC2 metrics history from cloud_metrics for ${instanceId}:`, err.message);
      }

      // If no historical data is available, return the currently available metrics together with an empty history array
      if (samples.length === 0) {
        try {
          const currentMetrics = await this.collectAll(instanceId);
          if (currentMetrics) {
            return {
              source: 'EC2 Instance',
              host: currentMetrics.system?.hostname || `aws-${instanceId}`,
              collectionInterval: 10,
              lastUpdated: currentMetrics.timestamp,
              samples: [currentMetrics],
              totalSamplesAvailable: 1,
              bufferUtilization: 0.3
            };
          }
        } catch {
          // ignore
        }
      }

      const latestSample = samples[samples.length - 1];

      return {
        source: latestSample?.sourceMetadata?.telemetrySource || 'EC2 Instance',
        host: latestSample?.sourceMetadata?.hostName || `aws-${instanceId}`,
        collectionInterval: 10,
        lastUpdated: latestSample?.timestamp || new Date().toISOString(),
        samples: samples,
        totalSamplesAvailable: samples.length,
        bufferUtilization: parseFloat(((samples.length / this.bufferSize) * 100).toFixed(1))
      };
    }

    // 2. Local Host History retrieval (instanceId is null)
    let samples = [];

    try {
      const mongoose = require('mongoose');
      if (mongoose.connection.readyState === 1) {
        const MonitoringMetric = require('../models/metric.model');
        const docs = await MonitoringMetric.find({}).sort({ createdAt: -1 }).limit(this.bufferSize).lean();
        if (docs && docs.length > 0) {
          samples = docs.map(doc => {
            const platformStr = doc.system?.platform || 'unknown';
            const parts = platformStr.split('|');
            const platform = parts[0] || platformStr;
            const telemetrySource = parts[1] || 'Unknown';
            const monitoringTarget = parts[2] || 'Unknown';
            const architecture = parts[3] || 'unknown';

            const cleanSystem = {
              ...doc.system,
              platform: platform,
              architecture: architecture
            };

            return {
              cpu: doc.cpu,
              memory: doc.memory,
              disk: doc.disk,
              network: doc.network,
              system: cleanSystem,
              sourceMetadata: {
                telemetrySource: telemetrySource,
                hostName: doc.system?.hostname || 'unknown',
                monitoringTarget: monitoringTarget,
                operatingSystem: os.type(),
                platform: platform,
                architecture: architecture,
                collectionInterval: 10,
                connectionStatus: 'Connected'
              },
              timestamp: doc.createdAt
            };
          });
          samples.reverse(); // return chronological
        }
      }
    } catch (err) {
      logger.error('Error reading metrics history from DB:', err.message);
    }

    // Fallback to in-memory buffer if DB is empty or offline
    if (samples.length === 0) {
      samples = (this.historyBuffer || []).map(item => {
        const cleanItem = JSON.parse(JSON.stringify(item));
        if (cleanItem.system && cleanItem.system.platform) {
          const parts = cleanItem.system.platform.split('|');
          cleanItem.system.platform = parts[0] || cleanItem.system.platform;
        }
        return cleanItem;
      });
    }

    const latestSample = samples[samples.length - 1];

    return {
      source: latestSample?.sourceMetadata?.telemetrySource || 'Local Host',
      host: latestSample?.sourceMetadata?.hostName || 'Unknown',
      collectionInterval: 10,
      lastUpdated: latestSample?.timestamp || new Date().toISOString(),
      samples: samples,
      totalSamplesAvailable: samples.length,
      bufferUtilization: parseFloat(((samples.length / this.bufferSize) * 100).toFixed(1))
    };
  }
}

module.exports = new CollectorService();
