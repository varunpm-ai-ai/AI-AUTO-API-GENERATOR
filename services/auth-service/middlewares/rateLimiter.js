/**
 * Rate Limiting Middlewares for Auth Service
 * Protects against brute force attacks, credential stuffing, and DoS
 */
const rateLimit = require('express-rate-limit');
const config = require('../config/env');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');

// Standard API rate limiter
const apiLimiter = rateLimit({
  windowMs: config.RATE_LIMIT_WINDOW_MS,
  max: config.RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    return ApiResponse.error(
      res,
      HTTP_STATUS.TOO_MANY_REQUESTS,
      'Too many requests. Please slow down and try again later.',
      'RATE_LIMIT_EXCEEDED'
    );
  }
});

// Strict rate limiter for sensitive authentication endpoints (login, forgot-password, reset-password)
const authStrictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: config.NODE_ENV === 'test' ? 1000 : 10, // 10 attempts in prod/dev, lenient in tests
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    return ApiResponse.error(
      res,
      HTTP_STATUS.TOO_MANY_REQUESTS,
      'Too many failed attempts. Please try again after 15 minutes.',
      'AUTH_RATE_LIMIT_EXCEEDED'
    );
  }
});

module.exports = {
  apiLimiter,
  authStrictLimiter
};
