/**
 * Trusted Gateway Identity Context Middleware for Discovery Service
 */
const authContextMiddleware = (req, res, next) => {
  const userId = req.headers['x-authenticated-user-id'] || 'anonymous';
  const tenantId = req.headers['x-tenant-id'] || 'default-tenant';
  const authMethod = req.headers['x-auth-method'] || 'ANONYMOUS';

  let roles = ['user'];
  try {
    if (req.headers['x-authenticated-roles']) {
      roles = JSON.parse(req.headers['x-authenticated-roles']);
    }
  } catch (e) {
    roles = ['user'];
  }

  req.authContext = {
    userId,
    tenantId,
    authMethod,
    roles
  };

  next();
};

module.exports = authContextMiddleware;
