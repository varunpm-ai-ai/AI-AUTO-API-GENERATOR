/**
 * Discovery Service Microservice Entry Point
 * Implements Google Antigravity Discovery Service Architecture Specification
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const config = require('./config/env');
const logger = require('./config/logger');
const connectDB = require('./config/db');

const requestIdMiddleware = require('./middlewares/requestId');
const authContextMiddleware = require('./middlewares/authContext');
const errorHandler = require('./middlewares/errorHandler');
const routes = require('./routes');

const app = express();

// Security & Parsing Middlewares
app.use(helmet());
app.use(cors({ origin: '*', credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Tracing & Identity Pipeline
app.use(requestIdMiddleware);
app.use(authContextMiddleware);

// Dev Logging
if (config.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// Register Central Routes
app.use(routes);

// Error Normalization Middleware
app.use(errorHandler);

// Start server if main entry module
if (require.main === module) {
  connectDB();
  const server = app.listen(config.PORT, () => {
    logger.info(`===================================================`);
    logger.info(`🚀 Discovery Service Microservice running on port ${config.PORT}`);
    logger.info(`📍 Environment: ${config.NODE_ENV}`);
    logger.info(`===================================================`);
  });

  const gracefulShutdown = (signal) => {
    logger.warn(`Received ${signal}. Shutting down Discovery Service...`);
    server.close(() => {
      logger.info('HTTP server closed. Exiting process.');
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
}

module.exports = app;
