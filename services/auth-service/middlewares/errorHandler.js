/**
 * Centralized Error Normalizer Middleware for Auth Service
 */
const config = require('../config/env');
const logger = require('../config/logger');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiResponse = require('../utils/apiResponse');

const errorHandler = (err, req, res, next) => {
  const requestId = req.requestId || null;

  let statusCode = err.statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
  let errorCode = err.errorCode || 'AUTH_INTERNAL_ERROR';
  let message = err.message || 'An unexpected error occurred in Auth Service';
  let details = err.details || null;

  if (statusCode >= 500) {
    logger.error(`Auth Service Error [${errorCode}]: ${message}`, {
      requestId,
      path: req.originalUrl,
      method: req.method,
      statusCode,
      stack: err.stack,
      details
    });

    if (config.NODE_ENV === 'production') {
      message = 'An internal authentication error occurred. Please contact system administrator.';
      details = null;
    }
  }

  return ApiResponse.error(res, statusCode, message, errorCode, details, requestId);
};

module.exports = errorHandler;
