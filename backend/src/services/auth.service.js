const jwt = require('jsonwebtoken');
const userRepository = require('../repositories/user.repository');
const logger = require('../config/logger');

class AuthService {
  async registerUser(username, email, password, role) {
    // Check if user exists by email
    const emailExists = await userRepository.findByEmail(email);
    if (emailExists) {
      const err = new Error('Email is already registered');
      err.statusCode = 400;
      throw err;
    }

    // Check if user exists by username
    const usernameExists = await userRepository.findByUsername(username);
    if (usernameExists) {
      const err = new Error('Username is already taken');
      err.statusCode = 400;
      throw err;
    }

    // Create user
    const user = await userRepository.create({ username, email, password, role });
    logger.info(`User registered successfully: ${user.username} (${user.role})`);
    
    // Sign JWT
    const token = this.generateToken(user._id, user.role);
    return {
      userId: user._id,
      username: user.username,
      email: user.email,
      role: user.role,
      token
    };
  }

  async loginUser(email, password) {
    const user = await userRepository.findByEmail(email);
    if (!user) {
      const err = new Error('Invalid email or password');
      err.statusCode = 401;
      throw err;
    }

    const isMatch = await user.matchPassword(password);
    if (!isMatch) {
      const err = new Error('Invalid email or password');
      err.statusCode = 401;
      throw err;
    }

    logger.info(`User logged in successfully: ${user.username}`);
    const token = this.generateToken(user._id, user.role);
    return {
      userId: user._id,
      username: user.username,
      email: user.email,
      role: user.role,
      token
    };
  }

  async getUserProfile(userId) {
    const user = await userRepository.findById(userId);
    if (!user) {
      const err = new Error('User not found');
      err.statusCode = 404;
      throw err;
    }
    return user;
  }

  generateToken(userId, role) {
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      throw new Error('JWT_SECRET is not defined in environment variables');
    }
    const expiresIn = process.env.JWT_EXPIRE || '1d';
    return jwt.sign({ id: userId, role }, secret, { expiresIn });
  }
}

module.exports = new AuthService();
