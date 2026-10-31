/**
 * Tenant Management Service
 * Manages tenant workspaces and guarantees multi-tenant boundaries
 */
const { v4: uuidv4 } = require('uuid');
const Storage = require('../models/storage');
const ApiError = require('../utils/apiError');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const AUTH_CONSTANTS = require('../constants/authConstants');

class TenantService {
  /**
   * Creates a new Tenant workspace
   */
  static async createTenant({ name, slug, plan = 'starter', settings = {} }) {
    if (!name || name.trim().length === 0) {
      throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'Tenant name is required', 'INVALID_TENANT_NAME');
    }

    const normalizedSlug = (slug || name)
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9-]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');

    const existing = await Storage.findTenantBySlug(normalizedSlug);
    if (existing) {
      throw new ApiError(HTTP_STATUS.CONFLICT, `Tenant workspace with slug '${normalizedSlug}' already exists`, 'TENANT_EXISTS');
    }

    const tenantId = `tnt_${uuidv4().replace(/-/g, '').slice(0, 16)}`;
    const tenant = await Storage.createTenant({
      tenantId,
      name: name.trim(),
      slug: normalizedSlug,
      plan,
      status: AUTH_CONSTANTS.TENANT_STATUS.ACTIVE,
      settings: {
        maxUsers: settings.maxUsers || 50,
        allowedDomains: settings.allowedDomains || [],
        requireMFA: settings.requireMFA || false
      }
    });

    return tenant;
  }

  /**
   * Retrieves tenant by ID
   */
  static async getTenantById(tenantId) {
    const tenant = await Storage.findTenantById(tenantId);
    if (!tenant) {
      throw new ApiError(HTTP_STATUS.NOT_FOUND, 'Tenant workspace not found', 'TENANT_NOT_FOUND');
    }
    return tenant;
  }

  /**
   * Retrieves tenant by slug
   */
  static async getTenantBySlug(slug) {
    const tenant = await Storage.findTenantBySlug(slug);
    if (!tenant) {
      throw new ApiError(HTTP_STATUS.NOT_FOUND, `Tenant workspace '${slug}' not found`, 'TENANT_NOT_FOUND');
    }
    return tenant;
  }

  /**
   * Verifies user membership within a specific tenant boundary
   */
  static async verifyTenantAccess(userId, tenantId, requiredRole = null) {
    const user = await Storage.findUserById(userId);
    if (!user) {
      return { hasAccess: false, reason: 'User does not exist' };
    }

    if (user.status !== AUTH_CONSTANTS.USER_STATUS.ACTIVE) {
      return { hasAccess: false, reason: 'User account is inactive or suspended' };
    }

    if (user.tenantId !== tenantId) {
      return { hasAccess: false, reason: 'Tenant boundary violation: User does not belong to this tenant' };
    }

    const tenant = await Storage.findTenantById(tenantId);
    if (!tenant || tenant.status !== AUTH_CONSTANTS.TENANT_STATUS.ACTIVE) {
      return { hasAccess: false, reason: 'Tenant workspace is inactive or suspended' };
    }

    if (requiredRole && user.role !== requiredRole && user.role !== AUTH_CONSTANTS.ROLES.TENANT_ADMIN) {
      return { hasAccess: false, reason: `Insufficient role: Required ${requiredRole}, has ${user.role}` };
    }

    return { hasAccess: true, reason: 'Access granted' };
  }
}

module.exports = TenantService;
