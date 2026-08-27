const request = require('supertest');
const app = require('../backend/app');
const mongoose = require('mongoose');

jest.mock('../backend/src/config/database', () => ({
  connect: jest.fn().mockResolvedValue(),
  disconnect: jest.fn().mockResolvedValue()
}));

describe('Integrated DevSecOps System Pipeline Tests', () => {
  beforeAll(async () => {
    mongoose.connection._readyState = 1;
  });

  afterAll(async () => {
    mongoose.connection._readyState = 0;
  });

  it('GET /system/status should query and aggregate service health statuses', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'OK', version: '1.0.0' })
      });
    });

    const res = await request(app).get('/system/status');
    
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.services.backend.status).toEqual('healthy');
    expect(res.body.services.monitoring.status).toEqual('healthy');
    expect(res.body.services.prometheus.status).toEqual('healthy');
  });

  it('POST /pipeline/analyze should execute the complete threat analysis pipeline', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes(':6001')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'success',
            data: {
              cpu: { utilization: 15.5 },
              memory: { usagePercent: 42.0 },
              disk: { usagePercent: 50.0 },
              network: { bytesRx: 1000, bytesTx: 2000 }
            }
          })
        });
      } else if (url.includes(':8000')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            is_anomaly: false,
            reconstruction_loss: 0.02
          })
        });
      } else if (url.includes(':8500')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            urs: 12.5,
            decision: 'Normal',
            reason: 'Baseline telemetry profile'
          })
        });
      }
      return Promise.reject(new Error('Unknown service url'));
    });

    const res = await request(app).post('/pipeline/analyze');
    
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.risk_score).toEqual(12.5);
    expect(res.body.decision).toEqual('Normal');
    expect(res.body.correlationId).toBeDefined();
  });

  it('POST /pipeline/analyze should recover gracefully (return 502) if AI engine is down', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes(':6001')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'success',
            data: {
              cpu: { utilization: 15.5 },
              memory: { usagePercent: 42.0 },
              disk: { usagePercent: 50.0 },
              network: { bytesRx: 1000, bytesTx: 2000 }
            }
          })
        });
      } else if (url.includes(':8000')) {
        return Promise.resolve({
          ok: false,
          status: 500
        });
      }
      return Promise.reject(new Error('Service unreachable'));
    });

    const res = await request(app).post('/pipeline/analyze');
    
    expect(res.statusCode).toEqual(502);
    expect(res.body.status).toEqual('error');
    expect(res.body.message).toContain('AI Engine prediction failed');
  });
});
