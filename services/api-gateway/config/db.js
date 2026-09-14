/**
 * Database Connection Module for API Gateway (MongoDB/Mongoose)
 */
const mongoose = require('mongoose');
const config = require('./env');
const logger = require('./logger');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(config.MONGO_URI, {
      serverSelectionTimeoutMS: 5000
    });

    logger.info(`MongoDB Connected to API Gateway DB: ${conn.connection.host}/${conn.connection.name}`);

    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB connection error:', { error: err.message });
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB disconnected. Retrying connection...');
    });

    return conn;
  } catch (error) {
    logger.error('Failed to connect to MongoDB for API Gateway:', { error: error.message });
    // In dev mode, do not crash hard if DB is optional or offline; allow in-memory/mock fallback
    if (config.NODE_ENV === 'production') {
      process.exit(1);
    }
  }
};

module.exports = connectDB;
