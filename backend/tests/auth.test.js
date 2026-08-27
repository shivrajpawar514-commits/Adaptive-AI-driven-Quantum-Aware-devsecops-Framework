const request = require('supertest');
const app = require('../app');
const database = require('../src/config/database');

// Mock database connection
jest.mock('../src/config/database', () => ({
  connect: jest.fn().mockResolvedValue(),
  disconnect: jest.fn().mockResolvedValue()
}));

// In-memory mock user database
const usersDb = [];

// Mock user repository to avoid database dependency during tests
jest.mock('../src/repositories/user.repository', () => {
  const bcrypt = require('bcryptjs');
  return {
    create: jest.fn().mockImplementation(async (userData) => {
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(userData.password, salt);
      const newUser = {
        _id: 'mock_user_id_' + Date.now(),
        username: userData.username,
        email: userData.email,
        password: hashedPassword,
        role: userData.role || 'Viewer',
        matchPassword: async function(enteredPassword) {
          return bcrypt.compare(enteredPassword, this.password);
        }
      };
      usersDb.push(newUser);
      return newUser;
    }),
    findByEmail: jest.fn().mockImplementation(async (email) => {
      return usersDb.find(u => u.email === email) || null;
    }),
    findByUsername: jest.fn().mockImplementation(async (username) => {
      return usersDb.find(u => u.username === username) || null;
    }),
    findById: jest.fn().mockImplementation(async (id) => {
      const user = usersDb.find(u => u._id === id);
      if (!user) return null;
      return {
        _id: user._id,
        username: user.username,
        email: user.email,
        role: user.role
      };
    })
  };
});

describe('Authentication API Flow', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  const testUser = {
    username: 'testadmin',
    email: 'testadmin@university.edu',
    password: 'Password123!',
    role: 'Admin'
  };

  it('should register a new user successfully', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send(testUser);

    expect(res.statusCode).toEqual(201);
    expect(res.body.status).toEqual('success');
    expect(res.body.data).toHaveProperty('token');
    expect(res.body.data.username).toEqual(testUser.username);
  });

  it('should fail to register a duplicate email', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send(testUser);

    expect(res.statusCode).toEqual(400);
    expect(res.body.status).toEqual('error');
  });

  it('should login successfully with correct credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: testUser.password
      });

    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data).toHaveProperty('token');
  });

  it('should reject login with wrong password', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: 'WrongPassword!'
      });

    expect(res.statusCode).toEqual(401);
    expect(res.body.status).toEqual('error');
  });

  it('should fetch user profile when authenticated', async () => {
    const loginRes = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: testUser.password
      });
    const token = loginRes.body.data.token;

    const res = await request(app)
      .get('/api/auth/profile')
      .set('Authorization', `Bearer ${token}`);

    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('success');
    expect(res.body.data.username).toEqual(testUser.username);
  });

  it('should reject profile access without token', async () => {
    const res = await request(app).get('/api/auth/profile');
    expect(res.statusCode).toEqual(401);
  });
});
