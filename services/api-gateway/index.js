/**
 * API Gateway Microservice Entry Point
 * Implements Google Antigravity API Gateway Architecture Specification
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const config = require('./config/env');
const logger = require('./config/logger');
const connectDB = require('./config/db');

const requestIdMiddleware = require('./middlewares/requestId');
const { authenticate } = require('./middlewares/auth');
const errorHandler = require('./middlewares/errorHandler');
const auditLogService = require('./services/auditLogService');
const routes = require('./routes');

const app = express();

// Security Middlewares
app.use(helmet());
app.use(
  cors({
    origin: config.ALLOWED_ORIGINS === '*' ? '*' : config.ALLOWED_ORIGINS.split(','),
    credentials: true
  })
);

// Body Parsing Middlewares
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request ID & Correlation Tracing Pipeline
app.use(requestIdMiddleware);

// Authentication & Identity Context Pipeline
app.use(authenticate);

// Request Audit & Access Logging Interceptor
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    auditLogService.logAccess(req, res, duration);
  });
  next();
});

// HTTP Request Logging in development
if (config.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// Register Gateway Routes
app.use(routes);

// Centralized Error Normalizer Handler (Must be registered last)
app.use(errorHandler);

// Start server if main entry module
if (require.main === module) {
  connectDB();
  const server = app.listen(config.PORT, () => {
    logger.info(`===================================================`);
    logger.info(`🚀 API Gateway Microservice running on port ${config.PORT}`);
    logger.info(`📍 Environment: ${config.NODE_ENV}`);
    logger.info(`📍 Gateway Prefix: ${config.GATEWAY_PREFIX}`);
    logger.info(`===================================================`);
  });

  const gracefulShutdown = (signal) => {
    logger.warn(`Received ${signal}. Shutting down API Gateway gracefully...`);
    server.close(() => {
      logger.info('HTTP server closed. Exiting process.');
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
}

module.exports = app;
