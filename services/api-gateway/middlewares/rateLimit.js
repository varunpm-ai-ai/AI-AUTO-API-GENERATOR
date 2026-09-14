/**
 * Rate Limiting Middleware for API Gateway
 * Implements Section 4.4 of API Gateway Implementation Spec.
 */
const rateLimit = require('express-rate-limit');
const config = require('../config/env');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');

const createGatewayRateLimiter = (options = {}) => {
  const windowMs = options.windowMs || config.RATE_LIMIT_WINDOW_MS;
  const max = options.max || config.RATE_LIMIT_MAX;

  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req) => {
      // Limit by API Key ID if present, otherwise User ID, otherwise Client IP
      if (req.gatewayContext && req.gatewayContext.apiKeyId) {
        return `apikey:${req.gatewayContext.apiKeyId}`;
      }
      if (req.gatewayContext && req.gatewayContext.userId) {
        return `user:${req.gatewayContext.userId}`;
      }
      return `ip:${req.ip || req.headers['x-forwarded-for'] || req.socket.remoteAddress}`;
    },
    handler: (req, res) => {
      const retryAfterSeconds = Math.ceil(windowMs / 1000);
      res.setHeader('Retry-After', retryAfterSeconds);
      res.status(HTTP_STATUS.TOO_MANY_REQUESTS).json({
        success: false,
        error: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: RESPONSE_MESSAGES.RATE_LIMIT_EXCEEDED,
          retry_after_seconds: retryAfterSeconds,
          request_id: req.requestId || req.headers['x-request-id'] || null,
          timestamp: new Date().toISOString()
        }
      });
    }
  });
};

module.exports = {
  gatewayRateLimiter: createGatewayRateLimiter(),
  createGatewayRateLimiter
};
