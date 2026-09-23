/**
 * Database Connection Module for Discovery Service
 */
const mongoose = require('mongoose');
const config = require('./env');
const logger = require('./logger');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(config.MONGO_URI, {
      serverSelectionTimeoutMS: 5000
    });

    logger.info(`MongoDB Connected to Discovery Service DB: ${conn.connection.host}/${conn.connection.name}`);

    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB Discovery Service DB connection error:', { error: err.message });
    });

    return conn;
  } catch (error) {
    logger.error('Failed to connect to MongoDB for Discovery Service:', { error: error.message });
    if (config.NODE_ENV === 'production') {
      process.exit(1);
    }
  }
};

module.exports = connectDB;
