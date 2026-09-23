/**
 * Centralized Error Normalizer Middleware for Discovery Service
 */
const config = require('../config/env');
const logger = require('../config/logger');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');
const ApiResponse = require('../utils/apiResponse');

const errorHandler = (err, req, res, next) => {
  const requestId = req.requestId || null;

  let statusCode = err.statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
  let errorCode = err.errorCode || 'DISCOVERY_INTERNAL_ERROR';
  let message = err.message || RESPONSE_MESSAGES.INTERNAL_ERROR;
  let details = err.details || null;

  logger.error(`Discovery Service Error [${errorCode}]: ${message}`, {
    requestId,
    path: req.originalUrl,
    method: req.method,
    statusCode,
    stack: err.stack,
    details
  });

  if (config.NODE_ENV === 'production' && statusCode === HTTP_STATUS.INTERNAL_SERVER_ERROR) {
    message = RESPONSE_MESSAGES.INTERNAL_ERROR;
    details = null;
  }

  return ApiResponse.error(res, statusCode, message, errorCode, details, requestId);
};

module.exports = errorHandler;
