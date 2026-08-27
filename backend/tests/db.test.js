const database = require('../src/config/database');

jest.mock('mongoose', () => {
  const mockState = { readyState: 0 };
  return {
    connection: mockState,
    connect: jest.fn().mockImplementation(() => {
      mockState.readyState = 1;
      return Promise.resolve();
    }),
    disconnect: jest.fn().mockImplementation(() => {
      mockState.readyState = 0;
      return Promise.resolve();
    }),
    Schema: jest.fn(),
    model: jest.fn()
  };
});

const mongoose = require('mongoose');

describe('Database Connection', () => {
  it('should connect and disconnect successfully', async () => {
    await database.connect();
    expect(mongoose.connection.readyState).toBe(1);
    await database.disconnect();
    expect(mongoose.connection.readyState).toBe(0);
  });
});
