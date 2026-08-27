const jwt = require('jsonwebtoken');
const logger = require('../config/logger');

const protect = (req, res, next) => {
  let token;
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (!token) {
    return res.status(401).json({ status: 'error', message: 'Not authorized to access this resource' });
  }

  try {
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      return res.status(500).json({ status: 'error', message: 'JWT_SECRET is not defined' });
    }
    const decoded = jwt.verify(token, secret);
    req.user = decoded;
    next();
  } catch (err) {
    logger.error(`JWT validation error: ${err.message}`);
    return res.status(401).json({ status: 'error', message: 'Token is invalid or expired' });
  }
};

const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ status: 'error', message: `User role '${req.user ? req.user.role : 'None'}' is not authorized to access this route` });
    }
    next();
  };
};

module.exports = {
  protect,
  authorize
};
