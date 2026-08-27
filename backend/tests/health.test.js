const request = require('supertest');
const app = require('../app');

describe('GET /api/health', () => {
  it('should return 200 OK and version info', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('status', 'OK');
    expect(res.body).toHaveProperty('version', '1.0.0');
  });
});
