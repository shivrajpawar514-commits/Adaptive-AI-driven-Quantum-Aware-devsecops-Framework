const mongoose = require('mongoose');

const metricSchema = new mongoose.Schema(
  {
    cpu: {
      utilization: { type: Number, required: true },
      cores: { type: Number, required: true },
      speed: { type: Number }
    },
    memory: {
      total: { type: Number, required: true },
      free: { type: Number, required: true },
      used: { type: Number, required: true },
      usagePercent: { type: Number, required: true }
    },
    disk: {
      size: { type: Number, required: true },
      used: { type: Number, required: true },
      free: { type: Number, required: true },
      usagePercent: { type: Number, required: true }
    },
    network: {
      interface: { type: String },
      bytesRx: { type: Number, required: true },
      bytesTx: { type: Number, required: true },
      rxRate: { type: Number },
      txRate: { type: Number }
    },
    system: {
      hostname: { type: String, required: true },
      uptime: { type: Number, required: true },
      platform: { type: String }
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model('MonitoringMetric', metricSchema);
