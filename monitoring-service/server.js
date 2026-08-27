require('dotenv').config();
const app = require('./app');
const database = require('./src/config/database');
const scheduler = require('./src/services/scheduler.service');
const logger = require('./src/config/logger');

const PORT = process.env.PORT || 6001;

database.connect().then(() => {
  // Start automated scheduler
  scheduler.start();

  const server = app.listen(PORT, () => {
    logger.info(`Monitoring service running on port ${PORT}`);
  });

  const handleShutdown = async (signal) => {
    logger.info(`Received ${signal}. Graceful shutdown...`);
    scheduler.stop();
    server.close(async () => {
      logger.info('HTTP server closed.');
      try {
        await database.disconnect();
        logger.info('Mongoose disconnected.');
        process.exit(0);
      } catch (err) {
        logger.error('Error during shutdown:', err);
        process.exit(1);
      }
    });
  };

  process.on('SIGINT', () => handleShutdown('SIGINT'));
  process.on('SIGTERM', () => handleShutdown('SIGTERM'));
}).catch(err => {
  logger.error('Database connection failed. Exiting.', err);
  process.exit(1);
});
