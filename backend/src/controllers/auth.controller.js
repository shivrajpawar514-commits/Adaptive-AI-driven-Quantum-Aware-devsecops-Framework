const authService = require('../services/auth.service');
const { validationResult } = require('express-validator');

class AuthController {
  async register(req, res, next) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ status: 'error', errors: errors.array() });
      }

      const { username, email, password, role } = req.body;
      const result = await authService.registerUser(username, email, password, role);
      res.status(201).json({ status: 'success', data: result });
    } catch (err) {
      next(err);
    }
  }

  async login(req, res, next) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ status: 'error', errors: errors.array() });
      }

      const { email, password } = req.body;
      const result = await authService.loginUser(email, password);
      res.status(200).json({ status: 'success', data: result });
    } catch (err) {
      next(err);
    }
  }

  async profile(req, res, next) {
    try {
      const result = await authService.getUserProfile(req.user.id);
      res.status(200).json({ status: 'success', data: result });
    } catch (err) {
      next(err);
    }
  }

  async logout(req, res, next) {
    try {
      res.status(200).json({ status: 'success', message: 'Logged out successfully' });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AuthController();
