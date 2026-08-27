require('dotenv').config();
const app = require('./app');
const database = require('./src/config/database');
const logger = require('./src/config/logger');

const PORT = process.env.PORT || 5000;

// Initialize Database connection
database.connect().then(() => {
  const server = app.listen(PORT, () => {
    logger.info(`Server is running on port ${PORT} in ${process.env.NODE_ENV || 'development'} mode`);
  });

  const handleShutdown = async (signal) => {
    logger.info(`Received ${signal}. Starting graceful shutdown...`);
    server.close(async () => {
      logger.info('HTTP server closed.');
      try {
        await database.disconnect();
        logger.info('Database connection closed gracefully.');
        process.exit(0);
      } catch (err) {
        logger.error('Error during database disconnection:', err);
        process.exit(1);
      }
    });
    
    // Force shutdown if it takes too long
    setTimeout(() => {
      logger.error('Could not close connections in time, forcefully shutting down.');
      process.exit(1);
    }, 10000);
  };

  process.on('SIGINT', () => handleShutdown('SIGINT'));
  process.on('SIGTERM', () => handleShutdown('SIGTERM'));
}).catch(err => {
  logger.error('Failed to initialize database connection. Exiting.', err);
  process.exit(1);
});
