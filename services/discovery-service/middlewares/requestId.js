/**
 * Request ID Middleware for Discovery Service
 */
const { v4: uuidv4 } = require('uuid');

const requestIdMiddleware = (req, res, next) => {
  const incomingRequestId = req.headers['x-request-id'];
  const incomingCorrelationId = req.headers['x-correlation-id'];

  const requestId = incomingRequestId || uuidv4();
  const correlationId = incomingCorrelationId || requestId;

  req.requestId = requestId;
  req.correlationId = correlationId;

  res.setHeader('x-request-id', requestId);
  res.setHeader('x-correlation-id', correlationId);

  next();
};

module.exports = requestIdMiddleware;
