const mongoose = require('mongoose');
const logger = require('./logger');
const dotenv = require('dotenv');

dotenv.config();

const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) {
  logger.error('MONGO_URI is not defined in environment variables');
  process.exit(1);
}

const options = {
  maxPoolSize: 10,
  minPoolSize: 2,
  socketTimeoutMS: 45000,
  serverSelectionTimeoutMS: 5000
};

const connect = async (retries = 5, delay = 5000) => {
  for (let i = 0; i < retries; i++) {
    try {
      await mongoose.connect(MONGO_URI, options);
      logger.info('Database connection established successfully');
      return;
    } catch (err) {
      logger.error(`Database connection attempt ${i + 1} failed. Error: ${err.message}`);
      if (i < retries - 1) {
        logger.info(`Retrying in ${delay / 1000} seconds...`);
        await new Promise((resolve) => setTimeout(resolve, delay));
      } else {
        throw err;
      }
    }
  }
};

const disconnect = async () => {
  try {
    await mongoose.disconnect();
    logger.info('Database disconnected successfully');
  } catch (err) {
    logger.error('Error disconnecting database:', err);
    throw err;
  }
};

module.exports = {
  connect,
  disconnect
};
