const express = require('express');
const router = express.Router();

/**
 * @openapi
 * /health:
 *   get:
 *     summary: Health check endpoint
 *     description: Checks status of api server
 *     responses:
 *       200:
 *         description: Server is online
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: OK
 *                 version:
 *                   type: string
 *                   example: 1.0.0
 */
router.get('/', (req, res) => {
  res.status(200).json({
    status: 'OK',
    version: '1.0.0'
  });
});

module.exports = router;
