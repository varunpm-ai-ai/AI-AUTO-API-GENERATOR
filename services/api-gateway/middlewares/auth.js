/**
 * Identity & Authentication Middleware for API Gateway
 * Implements Section 4.2 & Section 9 of API Gateway Implementation Spec.
 */
const jwt = require('jsonwebtoken');
const config = require('../config/env');
const API_CONSTANTS = require('../constants/apiConstants');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiError = require('../utils/apiError');
const apiKeyService = require('../services/apiKeyService');

const authenticate = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const rawApiKey = req.headers[API_CONSTANTS.HEADER_API_KEY] || req.headers['x-api-key'];

    // Default context for anonymous clients
    req.gatewayContext = {
      userId: null,
      tenantId: req.headers[API_CONSTANTS.HEADER_TENANT_ID] || 'default-tenant',
      roles: ['anonymous'],
      apiKeyId: null,
      authMethod: API_CONSTANTS.AUTH_METHOD_ANONYMOUS,
      requestId: req.requestId,
      correlationId: req.correlationId
    };

    // 1. Authenticate via JWT Token if Authorization header is present
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1];
      try {
        const decoded = jwt.verify(token, config.JWT_SECRET);
        req.gatewayContext.userId = decoded.sub || decoded.userId || decoded.id;
        req.gatewayContext.roles = decoded.roles || ['user'];
        req.gatewayContext.tenantId = decoded.tenantId || req.gatewayContext.tenantId;
        req.gatewayContext.authMethod = API_CONSTANTS.AUTH_METHOD_JWT;
        return next();
      } catch (err) {
        return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Invalid or expired JWT access token', 'TOKEN_EXPIRED'));
      }
    }

    // 2. Authenticate via API Key if header present
    if (rawApiKey) {
      const keyRecord = await apiKeyService.verifyKey(rawApiKey);
      if (!keyRecord) {
        return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Invalid or revoked API key', 'INVALID_API_KEY'));
      }

      req.gatewayContext.userId = keyRecord.ownerId;
      req.gatewayContext.apiKeyId = keyRecord._id.toString();
      req.gatewayContext.tenantId = keyRecord.tenantId || 'default-tenant';
      req.gatewayContext.roles = keyRecord.scopes || ['api_user'];
      req.gatewayContext.authMethod = API_CONSTANTS.AUTH_METHOD_API_KEY;
      return next();
    }

    // Anonymous request allowed to pass to next middleware (route authorization will check if required)
    return next();
  } catch (error) {
    return next(error);
  }
};

/**
 * Requires authenticated context for protected routes
 */
const requireAuth = (req, res, next) => {
  if (req.gatewayContext.authMethod === API_CONSTANTS.AUTH_METHOD_ANONYMOUS) {
    return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Authentication required to access this gateway route', 'UNAUTHORIZED_ACCESS'));
  }
  next();
};

module.exports = {
  authenticate,
  requireAuth
};
