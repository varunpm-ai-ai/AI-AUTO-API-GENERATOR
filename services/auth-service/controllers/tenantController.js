/**
 * Tenant Controller
 * Enforces Multi-Tenant Boundary Isolation and Member Management
 */
const { z } = require('zod');
const TenantService = require('../services/tenantService');
const AuthService = require('../services/authService');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const AUTH_CONSTANTS = require('../constants/authConstants');

const inviteMemberSchema = z.object({
  body: z.object({
    email: z.string().email('Please provide a valid email address').trim().toLowerCase(),
    name: z.string().min(2, 'Name must be at least 2 characters long').trim(),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters long')
      .regex(/[A-Za-z]/, 'Password must contain at least one letter')
      .regex(/[0-9]/, 'Password must contain at least one digit'),
    role: z
      .enum([AUTH_CONSTANTS.ROLES.DEVELOPER, AUTH_CONSTANTS.ROLES.VIEWER, AUTH_CONSTANTS.ROLES.TENANT_ADMIN])
      .default(AUTH_CONSTANTS.ROLES.DEVELOPER)
  })
});

class TenantController {
  /**
   * GET /api/v1/auth/tenants/current
   * Retrieves tenant details for the authenticated user's organization
   */
  static async getCurrentTenant(req, res, next) {
    try {
      const tenant = await TenantService.getTenantById(req.user.tenantId);
      return ApiResponse.success(res, 'Tenant details retrieved', tenant, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * GET /api/v1/auth/tenants/current/members
   * Retrieves members belonging strictly to the caller's tenant
   */
  static async getCurrentTenantMembers(req, res, next) {
    try {
      const members = await AuthService.getTenantMembers(req.user.tenantId);
      return ApiResponse.success(res, 'Tenant members retrieved', {
        tenantId: req.user.tenantId,
        memberCount: members.length,
        members
      }, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/tenants/current/members
   * Invites or creates a new member inside the caller's tenant workspace
   */
  static async inviteMember(req, res, next) {
    try {
      const member = await AuthService.addTenantMember(
        req.user.userId,
        req.user.tenantId,
        req.body
      );
      return ApiResponse.success(res, 'Tenant member added successfully', member, HTTP_STATUS.CREATED);
    } catch (error) {
      next(error);
    }
  }
}

module.exports = {
  TenantController,
  inviteMemberSchema
};
