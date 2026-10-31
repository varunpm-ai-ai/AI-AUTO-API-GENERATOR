/**
 * Authentication & Multi-Tenancy System Constants
 */
const AUTH_CONSTANTS = Object.freeze({
  ROLES: {
    TENANT_ADMIN: 'tenant_admin',
    DEVELOPER: 'developer',
    VIEWER: 'viewer',
    SYSTEM_ADMIN: 'system_admin'
  },

  TENANT_STATUS: {
    ACTIVE: 'ACTIVE',
    SUSPENDED: 'SUSPENDED',
    PENDING: 'PENDING'
  },

  USER_STATUS: {
    ACTIVE: 'ACTIVE',
    INACTIVE: 'INACTIVE',
    SUSPENDED: 'SUSPENDED'
  },

  DEFAULT_TENANT_ID: 'default-tenant',
  BCRYPT_SALT_ROUNDS: 12,
  RESET_TOKEN_BYTES: 32,
  REFRESH_TOKEN_BYTES: 40,

  HEADER_REQUEST_ID: 'x-request-id',
  HEADER_CORRELATION_ID: 'x-correlation-id',
  HEADER_TENANT_ID: 'x-tenant-id',
  HEADER_USER_ID: 'x-authenticated-user-id',
  HEADER_ROLES: 'x-authenticated-roles',
  HEADER_AUTH_METHOD: 'x-auth-method'
});

module.exports = AUTH_CONSTANTS;
