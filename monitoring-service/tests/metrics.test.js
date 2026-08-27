const request = require('supertest');
const app = require('../app');

jest.mock('../src/config/database', () => ({
  connect: jest.fn().mockResolvedValue(),
  disconnect: jest.fn().mockResolvedValue()
}));

jest.mock('../src/services/collector.service', () => ({
  collectAll: jest.fn().mockResolvedValue({
    cpu: { utilization: 10.5, cores: 4, speed: 2500 },
    memory: { total: 8589934592, free: 4294967296, used: 4294967296, usagePercent: 50.0 },
    disk: { size: 107374182400, used: 53687091200, free: 53687091200, usagePercent: 50.0 },
    network: { interface: 'eth0', bytesRx: 1024, bytesTx: 2048, rxRate: 0, txRate: 0 },
    system: { hostname: 'test-host', uptime: 3600, platform: 'linux' }
  })
}));

jest.mock('../src/models/metric.model', () => {
  return jest.fn().mockImplementation(() => ({
    save: jest.fn().mockResolvedValue()
  }));
});

describe('Monitoring Service Endpoints', () => {
  it('GET /health should return status OK', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('OK');
  });

  it('GET /metrics should return text format Prometheus scrape outputs', async () => {
    const res = await request(app).get('/metrics');
    expect(res.statusCode).toEqual(200);
    expect(res.headers['content-type']).toMatch(/text\/plain/);
  });

  it('GET /metrics/cpu should return CPU data', async () => {
    const res = await request(app).get('/metrics/cpu');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.utilization).toEqual(10.5);
  });

  it('GET /metrics/memory should return memory data', async () => {
    const res = await request(app).get('/metrics/memory');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.usagePercent).toEqual(50.0);
  });

  it('GET /metrics/disk should return disk data', async () => {
    const res = await request(app).get('/metrics/disk');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.usagePercent).toEqual(50.0);
  });

  it('GET /metrics/network should return network data', async () => {
    const res = await request(app).get('/metrics/network');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.interface).toEqual('eth0');
  });

  it('GET /metrics/system should return system data', async () => {
    const res = await request(app).get('/metrics/system');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.hostname).toEqual('test-host');
  });
});
