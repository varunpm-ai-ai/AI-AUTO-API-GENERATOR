/**
 * Authentication & Tenant Boundary Middleware for Auth Service
 */
const TokenUtils = require('../utils/tokenUtils');
const ApiError = require('../utils/apiError');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const AUTH_CONSTANTS = require('../constants/authConstants');

/**
 * Extracts and verifies JWT access token from Authorization header
 */
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    req.user = null;
    return next();
  }

  const token = authHeader.split(' ')[1];
  const decoded = TokenUtils.verifyAccessToken(token);

  if (!decoded) {
    return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Invalid or expired access token', 'TOKEN_EXPIRED'));
  }

  req.user = {
    userId: decoded.sub || decoded.userId,
    tenantId: decoded.tenantId,
    email: decoded.email,
    roles: Array.isArray(decoded.roles) ? decoded.roles : [decoded.role || 'viewer'],
    name: decoded.name
  };

  next();
};

/**
 * Enforces that client is authenticated
 */
const requireAuth = (req, res, next) => {
  if (!req.user || !req.user.userId) {
    return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Authentication required to access this resource', 'UNAUTHORIZED'));
  }
  next();
};

/**
 * Enforces role requirement (supports tenant_admin super-role)
 */
const requireRole = (...allowedRoles) => (req, res, next) => {
  if (!req.user || !req.user.userId) {
    return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Authentication required', 'UNAUTHORIZED'));
  }

  const hasRole = req.user.roles.some(
    (role) => allowedRoles.includes(role) || role === AUTH_CONSTANTS.ROLES.TENANT_ADMIN || role === AUTH_CONSTANTS.ROLES.SYSTEM_ADMIN
  );

  if (!hasRole) {
    return next(new ApiError(HTTP_STATUS.FORBIDDEN, 'You do not have permission to perform this action', 'FORBIDDEN'));
  }

  next();
};

/**
 * Enforces tenant boundary isolation
 */
const enforceTenantIsolation = (paramName = 'tenantId') => (req, res, next) => {
  if (!req.user || !req.user.userId) {
    return next(new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Authentication required', 'UNAUTHORIZED'));
  }

  const requestedTenantId = req.params[paramName] || req.body[paramName] || req.query[paramName];
  if (requestedTenantId && requestedTenantId !== req.user.tenantId && !req.user.roles.includes(AUTH_CONSTANTS.ROLES.SYSTEM_ADMIN)) {
    return next(
      new ApiError(
        HTTP_STATUS.FORBIDDEN,
        'Tenant isolation violation: Access denied to foreign tenant resources',
        'TENANT_ISOLATION_VIOLATION'
      )
    );
  }

  next();
};

module.exports = {
  authenticate,
  requireAuth,
  requireRole,
  enforceTenantIsolation
};
