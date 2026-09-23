/**
 * Operational ApiError Class for Discovery Service
 */
const HTTP_STATUS = require('../constants/httpStatusCodes');

class ApiError extends Error {
  constructor(statusCode, message, errorCode = 'INTERNAL_ERROR', details = null, isOperational = true) {
    super(message);
    this.statusCode = statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
    this.errorCode = errorCode;
    this.details = details;
    this.isOperational = isOperational;

    Error.captureStackTrace(this, this.constructor);
  }
}

module.exports = ApiError;
