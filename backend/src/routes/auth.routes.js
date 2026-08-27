const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const { registerValidator, loginValidator } = require('../validators/auth.validator');
const { protect } = require('../middlewares/auth.middleware');

/**
 * @openapi
 * /auth/register:
 *   post:
 *     summary: Register a new user
 *     description: Create username account
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - username
 *               - email
 *               - password
 *             properties:
 *               username:
 *                 type: string
 *                 example: security_guy
 *               email:
 *                 type: string
 *                 example: check@university.edu
 *               password:
 *                 type: string
 *                 example: StrongSecure123!
 *               role:
 *                 type: string
 *                 example: Researcher
 *     responses:
 *       201:
 *         description: User created
 *       400:
 *         description: Validation failed
 */
router.post('/register', registerValidator, authController.register);

/**
 * @openapi
 * /auth/login:
 *   post:
 *     summary: Authenticate user
 *     description: Log in using email and password
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - password
 *             properties:
 *               email:
 *                 type: string
 *                 example: check@university.edu
 *               password:
 *                 type: string
 *                 example: StrongSecure123!
 *     responses:
 *       200:
 *         description: Logged in
 *       401:
 *         description: Invalid credentials
 */
router.post('/login', loginValidator, authController.login);

/**
 * @openapi
 * /auth/profile:
 *   get:
 *     summary: Get user profile
 *     description: Returns authenticated user details
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Details returned
 *       401:
 *         description: Unauthorized
 */
router.get('/profile', protect, authController.profile);

/**
 * @openapi
 * /auth/logout:
 *   post:
 *     summary: Log out
 *     description: Log out active session
 *     responses:
 *       200:
 *         description: Logged out
 */
router.post('/logout', authController.logout);

module.exports = router;
