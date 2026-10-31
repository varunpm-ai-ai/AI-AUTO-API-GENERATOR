/**
 * Multi-Tenant Workspace & Member Routes
 */
const express = require('express');
const router = express.Router();

const { TenantController, inviteMemberSchema } = require('../controllers/tenantController');
const validateRequest = require('../middlewares/validateRequest');
const { authenticate, requireAuth, requireRole } = require('../middlewares/authMiddleware');
const AUTH_CONSTANTS = require('../constants/authConstants');

router.use(authenticate);
router.use(requireAuth);

// Current user's tenant details
router.get('/current', TenantController.getCurrentTenant);

// Members within the tenant boundary (strictly isolated)
router.get('/current/members', TenantController.getCurrentTenantMembers);

// Invite or add member to current tenant (restricted to tenant_admin)
router.post(
  '/current/members',
  requireRole(AUTH_CONSTANTS.ROLES.TENANT_ADMIN),
  validateRequest(inviteMemberSchema),
  TenantController.inviteMember
);

module.exports = router;
