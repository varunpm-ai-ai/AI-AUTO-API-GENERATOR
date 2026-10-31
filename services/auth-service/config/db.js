/**
 * Database Connection Module for Auth Service
 */
const mongoose = require('mongoose');
const config = require('./env');
const logger = require('./logger');

let isConnected = false;

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(config.MONGO_URI, {
      serverSelectionTimeoutMS: 2000
    });

    isConnected = true;
    logger.info(`MongoDB Connected to Auth Service DB: ${conn.connection.host}/${conn.connection.name}`);

    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB Auth Service DB connection error:', { error: err.message });
      isConnected = false;
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB Auth Service disconnected. Fallback memory store active.');
      isConnected = false;
    });

    return conn;
  } catch (error) {
    isConnected = false;
    logger.warn('MongoDB not available for Auth Service. Operating with persistent in-memory store.', {
      error: error.message
    });
    return null;
  }
};

const getDbStatus = () => isConnected;

module.exports = {
  connectDB,
  getDbStatus
};
