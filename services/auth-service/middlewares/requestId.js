/**
 * Request ID & Tracing Middleware for Auth Service
 */
const { v4: uuidv4 } = require('uuid');
const AUTH_CONSTANTS = require('../constants/authConstants');

const requestIdMiddleware = (req, res, next) => {
  const incomingRequestId = req.headers[AUTH_CONSTANTS.HEADER_REQUEST_ID];
  const incomingCorrelationId = req.headers[AUTH_CONSTANTS.HEADER_CORRELATION_ID];

  const requestId = incomingRequestId || uuidv4();
  const correlationId = incomingCorrelationId || requestId;

  req.requestId = requestId;
  req.correlationId = correlationId;

  res.setHeader(AUTH_CONSTANTS.HEADER_REQUEST_ID, requestId);
  res.setHeader(AUTH_CONSTANTS.HEADER_CORRELATION_ID, correlationId);

  next();
};

module.exports = requestIdMiddleware;
