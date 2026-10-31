/**
 * Authentication Microservice Entry Point
 * Exposes REST API (Port 5000) and gRPC Server (Port 50051)
 * Tailored for AI Auto API Generator Multi-Tenant Architecture
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const config = require('./config/env');
const logger = require('./config/logger');
const { connectDB } = require('./config/db');

const requestIdMiddleware = require('./middlewares/requestId');
const { apiLimiter } = require('./middlewares/rateLimiter');
const errorHandler = require('./middlewares/errorHandler');
const routes = require('./routes');
const AuthGrpcServer = require('./grpc/authGrpcServer');

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
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: true, limit: '2mb' }));

// Request Tracing Pipeline
app.use(requestIdMiddleware);

// Global Rate Limiting
app.use(apiLimiter);

// HTTP Logging in development
if (config.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// Register Application Routes
app.use(routes);

// Centralized Error Normalizer Handler (Must be registered last)
app.use(errorHandler);

// Standalone gRPC Server instance
const grpcServer = new AuthGrpcServer(config.GRPC_PORT);

// Start server if executed directly
if (require.main === module) {
  const startServers = async () => {
    // 1. Connect Database (or fallback memory)
    await connectDB();

    // 2. Start gRPC Server
    try {
      await grpcServer.start();
    } catch (grpcErr) {
      logger.error('Failed to start Auth gRPC Server:', { error: grpcErr.message });
    }

    // 3. Start HTTP Server
    const server = app.listen(config.PORT, () => {
      logger.info('===================================================');
      logger.info(`🚀 Auth Service REST API running on port ${config.PORT}`);
      logger.info(`⚡ Auth Service gRPC Server running on port ${config.GRPC_PORT}`);
      logger.info(`📍 Environment: ${config.NODE_ENV}`);
      logger.info('===================================================');
    });

    const gracefulShutdown = async (signal) => {
      logger.warn(`Received ${signal}. Shutting down Auth Service gracefully...`);
      await grpcServer.stop();
      server.close(() => {
        logger.info('HTTP server closed. Exiting process.');
        process.exit(0);
      });
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
  };

  startServers();
}

module.exports = {
  app,
  grpcServer
};
