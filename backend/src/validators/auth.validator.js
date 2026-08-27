const { body } = require('express-validator');

const registerValidator = [
  body('username')
    .isAlphanumeric()
    .withMessage('Username must be alphanumeric')
    .isLength({ min: 3, max: 30 })
    .withMessage('Username must be between 3 and 30 characters'),
  body('email')
    .isEmail()
    .withMessage('Provide a valid email address')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/[A-Z]/)
    .withMessage('Password must contain at least one uppercase letter')
    .matches(/[a-z]/)
    .withMessage('Password must contain at least one lowercase letter')
    .matches(/[0-9]/)
    .withMessage('Password must contain at least one number')
    .matches(/[\W]/)
    .withMessage('Password must contain at least one special character'),
  body('role')
    .optional()
    .isIn(['Admin', 'Researcher', 'Viewer'])
    .withMessage('Role must be one of Admin, Researcher, or Viewer')
];

const loginValidator = [
  body('email')
    .isEmail()
    .withMessage('Provide a valid email address')
    .normalizeEmail(),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

module.exports = {
  registerValidator,
  loginValidator
};
