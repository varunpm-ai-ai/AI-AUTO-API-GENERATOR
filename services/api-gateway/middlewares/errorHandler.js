/**
 * Centralized Error Normalization Middleware for API Gateway
 * Implements Section 4.7 of API Gateway Implementation Spec.
 */
const config = require('../config/env');
const logger = require('../config/logger');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');
const ApiResponse = require('../utils/apiResponse');

const errorHandler = (err, req, res, next) => {
  const requestId = req.requestId || (req.headers && req.headers['x-request-id']) || null;
  const correlationId = req.correlationId || requestId;

  let statusCode = err.statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
  let errorCode = err.errorCode || 'GATEWAY_INTERNAL_ERROR';
  let message = err.message || RESPONSE_MESSAGES.INTERNAL_ERROR;
  let details = err.details || null;

  // Log full error details internally without exposing them in response
  logger.error(`API Gateway Error [${errorCode}]: ${message}`, {
    requestId,
    correlationId,
    path: req.originalUrl,
    method: req.method,
    statusCode,
    stack: err.stack,
    details
  });

  // Handle Mongoose CastError / ValidationError
  if (err.name === 'CastError') {
    statusCode = HTTP_STATUS.BAD_REQUEST;
    errorCode = 'INVALID_RESOURCE_ID';
    message = 'Invalid resource identifier format';
  } else if (err.name === 'ValidationError') {
    statusCode = HTTP_STATUS.BAD_REQUEST;
    errorCode = 'VALIDATION_ERROR';
    message = 'Database model validation failed';
  }

  // Sanitize stack trace in production
  if (config.NODE_ENV === 'production' && statusCode === HTTP_STATUS.INTERNAL_SERVER_ERROR) {
    message = RESPONSE_MESSAGES.INTERNAL_ERROR;
    details = null;
  }

  return ApiResponse.error(res, statusCode, message, errorCode, details, requestId);
};

module.exports = errorHandler;
