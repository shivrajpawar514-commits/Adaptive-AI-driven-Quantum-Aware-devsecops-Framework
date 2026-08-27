const http = require('http');
const os = require('os');
const logger = require('../config/logger');

class SourceDetectionService {
  constructor() {
    this.cloudAdapterUrl = process.env.CLOUD_ADAPTER_URL || 'http://localhost:7000';
  }

  // Internal helper to perform HTTP GET requests returning JSON
  _fetchJson(url) {
    return new Promise((resolve, reject) => {
      const parsedUrl = new URL(url);
      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 80,
        path: parsedUrl.pathname + parsedUrl.search,
        method: 'GET',
        timeout: 8000 // 8 second timeout
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (err) {
            reject(new Error(`Failed to parse JSON response: ${err.message}`));
          }
        });
      });

      req.on('error', (err) => {
        reject(err);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timed out'));
      });

      req.end();
    });
  }

  async detectSource() {
    try {
      const assetsUrl = `${this.cloudAdapterUrl.replace(/\/$/, '')}/cloud/assets`;
      const res = await this._fetchJson(assetsUrl);
      
      if (res && res.status === 'success' && Array.isArray(res.data) && res.data.length > 0) {
        // Find the first active (running) EC2 instance
        const activeInstance = res.data.find(inst => inst.state === 'running') || res.data[0];
        if (activeInstance && activeInstance.instanceId) {
          logger.info(`[SourceDetection] Active EC2 Instance detected: ${activeInstance.instanceId}`);
          return {
            type: 'EC2 Instance',
            targetId: activeInstance.instanceId,
            hostname: activeInstance.instanceName || activeInstance.instanceId,
            platform: activeInstance.platform || 'linux',
            region: activeInstance.region || 'us-east-1',
            details: activeInstance
          };
        }
      }
    } catch (err) {
      logger.info(`[SourceDetection] Falling back to Local Host. Cloud Adapter status: ${err.message}`);
    }

    return {
      type: 'Local Host',
      targetId: '127.0.0.1',
      hostname: os.hostname(),
      platform: os.platform(),
      details: null
    };
  }
}

module.exports = new SourceDetectionService();
