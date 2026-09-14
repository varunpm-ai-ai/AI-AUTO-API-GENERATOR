/**
 * Request ID & Correlation ID Middleware for API Gateway
 * Implements Section 4.6 of API Gateway Implementation Spec.
 */
const { v4: uuidv4 } = require('uuid');
const API_CONSTANTS = require('../constants/apiConstants');

const requestIdMiddleware = (req, res, next) => {
  const incomingRequestId = req.headers[API_CONSTANTS.HEADER_REQUEST_ID];
  const incomingCorrelationId = req.headers[API_CONSTANTS.HEADER_CORRELATION_ID];

  const requestId = incomingRequestId || uuidv4();
  const correlationId = incomingCorrelationId || requestId;

  req.requestId = requestId;
  req.correlationId = correlationId;

  // Set response headers for client tracing
  res.setHeader(API_CONSTANTS.HEADER_REQUEST_ID, requestId);
  res.setHeader(API_CONSTANTS.HEADER_CORRELATION_ID, correlationId);

  next();
};

module.exports = requestIdMiddleware;
