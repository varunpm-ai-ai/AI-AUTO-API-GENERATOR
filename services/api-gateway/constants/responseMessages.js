/**
 * Standardized Response Messages Constants for API Gateway
 */
const RESPONSE_MESSAGES = Object.freeze({
  SUCCESS: 'Operation completed successfully',
  CREATED: 'Resource created successfully',
  UPDATED: 'Resource updated successfully',
  DELETED: 'Resource deleted successfully',
  FETCHED: 'Resource retrieved successfully',
  
  KEY_CREATED: 'API key generated successfully',
  KEY_REVOKED: 'API key revoked successfully',
  KEY_VALID: 'API key validated successfully',
  
  BAD_REQUEST: 'Invalid request headers, parameters or body payload',
  UNAUTHORIZED: 'Authentication token or API key required or invalid',
  FORBIDDEN: 'Access denied due to insufficient permissions or scopes',
  NOT_FOUND: 'Target gateway route or resource not found',
  RATE_LIMIT_EXCEEDED: 'Rate limit exceeded. Please wait before making more requests',
  INTERNAL_ERROR: 'An internal API Gateway error occurred',
  GATEWAY_PROXY_ERROR: 'Downstream service unavailable or failed to respond'
});

module.exports = RESPONSE_MESSAGES;
