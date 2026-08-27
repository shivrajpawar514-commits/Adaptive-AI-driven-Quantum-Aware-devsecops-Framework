const mongoose = require('mongoose');
const logger = require('./logger');

const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) {
  logger.error('MONGO_URI is not defined in environment variables');
  process.exit(1);
}

const connect = async (retries = 3, delay = 5000) => {
  for (let i = 0; i < retries; i++) {
    try {
      await mongoose.connect(MONGO_URI);
      logger.info('Monitoring service connected to MongoDB successfully');
      return;
    } catch (err) {
      logger.error(`Mongoose connection error (attempt ${i + 1}): ${err.message}`);
      if (i < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw err;
      }
    }
  }
};

const disconnect = async () => {
  try {
    await mongoose.disconnect();
    logger.info('Mongoose disconnected.');
  } catch (err) {
    logger.error('Error disconnecting Mongoose:', err);
  }
};

module.exports = { connect, disconnect };
