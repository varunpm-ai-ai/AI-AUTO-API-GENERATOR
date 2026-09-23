/**
 * Rate Limit Middleware for Discovery Service
 */
const rateLimit = require('express-rate-limit');
const config = require('../config/env');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');

const discoveryRateLimiter = rateLimit({
  windowMs: config.RATE_LIMIT_WINDOW_MS,
  max: config.RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(HTTP_STATUS.TOO_MANY_REQUESTS).json({
      success: false,
      error: {
        code: 'RATE_LIMIT_EXCEEDED',
        message: RESPONSE_MESSAGES.RATE_LIMIT_EXCEEDED,
        request_id: req.requestId || null,
        timestamp: new Date().toISOString()
      }
    });
  }
});

module.exports = discoveryRateLimiter;
