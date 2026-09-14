/**
 * API Gateway System Headers & Constants
 */
const API_CONSTANTS = Object.freeze({
  DEFAULT_PORT: 4000,
  GATEWAY_PREFIX: '/api/v1/gateway',
  
  API_KEY_PREFIX: 'ak_',
  API_KEY_LENGTH: 32,
  
  HEADER_REQUEST_ID: 'x-request-id',
  HEADER_CORRELATION_ID: 'x-correlation-id',
  HEADER_API_KEY: 'x-api-key',
  HEADER_TENANT_ID: 'x-tenant-id',
  HEADER_USER_ID: 'x-authenticated-user-id',
  HEADER_ROLES: 'x-authenticated-roles',
  HEADER_AUTH_METHOD: 'x-auth-method',

  AUTH_METHOD_JWT: 'JWT',
  AUTH_METHOD_API_KEY: 'API_KEY',
  AUTH_METHOD_ANONYMOUS: 'ANONYMOUS',

  DEFAULT_TIMEOUT_MS: 15000
});

module.exports = API_CONSTANTS;
