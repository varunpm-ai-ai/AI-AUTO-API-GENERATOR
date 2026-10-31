/**
 * Core Authentication Service
 * Implements signup, login, password reset, token rotation, and multi-tenant isolation
 */
const { v4: uuidv4 } = require('uuid');
const config = require('../config/env');
const logger = require('../config/logger');
const Storage = require('../models/storage');
const TenantService = require('./tenantService');
const PasswordUtils = require('../utils/passwordUtils');
const TokenUtils = require('../utils/tokenUtils');
const ApiError = require('../utils/apiError');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const AUTH_CONSTANTS = require('../constants/authConstants');

class AuthService {
  /**
   * User Signup
   * Automatically creates a new Tenant if tenantName provided, or joins an existing tenant
   */
  static async signup({ email, password, name, tenantName, tenantSlug, role = null }) {
    const normalizedEmail = email.toLowerCase().trim();

    // Check if email already registered
    const existingUser = await Storage.findUserByEmail(normalizedEmail);
    if (existingUser) {
      throw new ApiError(
        HTTP_STATUS.CONFLICT,
        'An account with this email address already exists',
        'EMAIL_ALREADY_EXISTS'
      );
    }

    let tenant;
    let assignedRole = role || AUTH_CONSTANTS.ROLES.VIEWER;

    if (tenantSlug) {
      // Joining existing tenant
      tenant = await TenantService.getTenantBySlug(tenantSlug);
      if (tenant.status !== AUTH_CONSTANTS.TENANT_STATUS.ACTIVE) {
        throw new ApiError(HTTP_STATUS.FORBIDDEN, 'Tenant workspace is inactive', 'TENANT_INACTIVE');
      }
    } else {
      // Creating a new tenant workspace - first user becomes tenant_admin
      const orgName = tenantName || `${name.split(' ')[0]}'s Workspace`;
      tenant = await TenantService.createTenant({ name: orgName });
      assignedRole = AUTH_CONSTANTS.ROLES.TENANT_ADMIN;
    }

    // Hash password with bcrypt (12 salt rounds)
    const passwordHash = await PasswordUtils.hashPassword(password);
    const userId = `usr_${uuidv4().replace(/-/g, '').slice(0, 16)}`;

    // Generate rotated refresh token
    const { rawToken: rawRefreshToken, tokenHash, expiresAt } = TokenUtils.generateRefreshToken();
    const refreshTokens = [{
      tokenId: `rt_${uuidv4().replace(/-/g, '').slice(0, 12)}`,
      tokenHash,
      expiresAt,
      createdAt: new Date()
    }];

    // Persist new user
    const createdUser = await Storage.createUser({
      userId,
      tenantId: tenant.tenantId,
      email: normalizedEmail,
      passwordHash,
      name: name.trim(),
      role: assignedRole,
      status: AUTH_CONSTANTS.USER_STATUS.ACTIVE,
      refreshTokens
    });

    // Generate JWT access token
    const accessToken = TokenUtils.generateAccessToken({
      userId,
      tenantId: tenant.tenantId,
      email: normalizedEmail,
      role: assignedRole,
      name: createdUser.name
    });

    const sanitizedUser = Storage.sanitizeUser(createdUser);

    logger.info(`User signed up successfully: ${normalizedEmail} (Tenant: ${tenant.tenantId})`);

    return {
      user: sanitizedUser,
      tenant: {
        tenantId: tenant.tenantId,
        name: tenant.name,
        slug: tenant.slug,
        plan: tenant.plan
      },
      tokens: {
        accessToken,
        refreshToken: rawRefreshToken,
        expiresIn: config.JWT_EXPIRES_IN
      }
    };
  }

  /**
   * User Login
   * Constant-time password check, generic error messages to prevent enumeration
   */
  static async login({ email, password, tenantSlug = null }) {
    const normalizedEmail = email.toLowerCase().trim();

    // Find user (with sensitive fields for password verification)
    const user = await Storage.findUserByEmail(normalizedEmail, null, true);
    if (!user) {
      // Generic error message to prevent user enumeration
      throw new ApiError(
        HTTP_STATUS.UNAUTHORIZED,
        'Invalid email or password',
        'INVALID_CREDENTIALS'
      );
    }

    // Constant-time password verification
    const isPasswordValid = await PasswordUtils.verifyPassword(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new ApiError(
        HTTP_STATUS.UNAUTHORIZED,
        'Invalid email or password',
        'INVALID_CREDENTIALS'
      );
    }

    // Account status validation
    if (user.status !== AUTH_CONSTANTS.USER_STATUS.ACTIVE) {
      throw new ApiError(
        HTTP_STATUS.FORBIDDEN,
        'Your user account is suspended or inactive',
        'ACCOUNT_SUSPENDED'
      );
    }

    // Verify tenant
    const tenant = await TenantService.getTenantById(user.tenantId);
    if (tenant.status !== AUTH_CONSTANTS.TENANT_STATUS.ACTIVE) {
      throw new ApiError(
        HTTP_STATUS.FORBIDDEN,
        'Tenant workspace is suspended or inactive',
        'TENANT_SUSPENDED'
      );
    }

    if (tenantSlug && tenant.slug !== tenantSlug.toLowerCase().trim()) {
      throw new ApiError(
        HTTP_STATUS.FORBIDDEN,
        'User does not belong to the requested tenant workspace',
        'TENANT_MISMATCH'
      );
    }

    // Generate rotated refresh token
    const { rawToken: rawRefreshToken, tokenHash, expiresAt } = TokenUtils.generateRefreshToken();
    const now = new Date();

    // Clean up expired refresh tokens, keep last 5 active sessions
    const activeTokens = (user.refreshTokens || [])
      .filter((t) => new Date(t.expiresAt) > now)
      .slice(-4);

    activeTokens.push({
      tokenId: `rt_${uuidv4().replace(/-/g, '').slice(0, 12)}`,
      tokenHash,
      expiresAt,
      createdAt: now
    });

    await Storage.updateUser(user.userId, { refreshTokens: activeTokens });

    // Issue JWT Access Token
    const accessToken = TokenUtils.generateAccessToken({
      userId: user.userId,
      tenantId: tenant.tenantId,
      email: user.email,
      role: user.role,
      name: user.name
    });

    const sanitizedUser = Storage.sanitizeUser(user);

    logger.info(`User authenticated: ${normalizedEmail} (Tenant: ${tenant.tenantId})`);

    return {
      user: sanitizedUser,
      tenant: {
        tenantId: tenant.tenantId,
        name: tenant.name,
        slug: tenant.slug,
        plan: tenant.plan
      },
      tokens: {
        accessToken,
        refreshToken: rawRefreshToken,
        expiresIn: config.JWT_EXPIRES_IN
      }
    };
  }

  /**
   * Refresh Token Rotation
   * Single-use rotation: old token is invalidated, new pair returned
   */
  static async refreshToken(rawRefreshToken) {
    if (!rawRefreshToken) {
      throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'Refresh token is required', 'TOKEN_REQUIRED');
    }

    const tokenHash = PasswordUtils.hashToken(rawRefreshToken);
    const user = await Storage.findUserByRefreshToken(tokenHash, true);

    if (!user) {
      throw new ApiError(
        HTTP_STATUS.UNAUTHORIZED,
        'Invalid or expired refresh token. Please log in again.',
        'INVALID_REFRESH_TOKEN'
      );
    }

    const tenant = await TenantService.getTenantById(user.tenantId);
    if (tenant.status !== AUTH_CONSTANTS.TENANT_STATUS.ACTIVE) {
      throw new ApiError(HTTP_STATUS.FORBIDDEN, 'Tenant workspace is inactive', 'TENANT_INACTIVE');
    }

    // Rotate: remove old refresh token
    const now = new Date();
    const remainingTokens = (user.refreshTokens || []).filter(
      (t) => t.tokenHash !== tokenHash && new Date(t.expiresAt) > now
    );

    // Generate new rotated refresh token
    const { rawToken: newRawRefreshToken, tokenHash: newTokenHash, expiresAt } = TokenUtils.generateRefreshToken();
    remainingTokens.push({
      tokenId: `rt_${uuidv4().replace(/-/g, '').slice(0, 12)}`,
      tokenHash: newTokenHash,
      expiresAt,
      createdAt: now
    });

    await Storage.updateUser(user.userId, { refreshTokens: remainingTokens });

    // Issue new JWT access token
    const accessToken = TokenUtils.generateAccessToken({
      userId: user.userId,
      tenantId: tenant.tenantId,
      email: user.email,
      role: user.role,
      name: user.name
    });

    return {
      accessToken,
      refreshToken: newRawRefreshToken,
      expiresIn: config.JWT_EXPIRES_IN
    };
  }

  /**
   * Request Password Reset
   * Creates cryptographically secure random token, stores ONLY its SHA-256 hash
   * Prevents user enumeration by returning standard message even if email not found
   */
  static async requestPasswordReset(email) {
    const normalizedEmail = email.toLowerCase().trim();
    const user = await Storage.findUserByEmail(normalizedEmail, null, true);

    const genericResponse = {
      message: 'If an account with that email exists, password reset instructions have been generated.',
      email: normalizedEmail
    };

    if (!user) {
      // Return same response to prevent email harvesting
      return genericResponse;
    }

    // Generate 32-byte cryptographically random token
    const rawResetToken = PasswordUtils.generateRandomToken(AUTH_CONSTANTS.RESET_TOKEN_BYTES);
    const tokenHash = PasswordUtils.hashToken(rawResetToken);
    const expiresAt = new Date(Date.now() + config.RESET_TOKEN_EXPIRES_MINUTES * 60 * 1000);

    // Store ONLY the SHA-256 hash in database
    await Storage.updateUser(user.userId, {
      resetPasswordToken: tokenHash,
      resetPasswordExpires: expiresAt
    });

    logger.info(`Password reset token generated for ${normalizedEmail} (Expires in ${config.RESET_TOKEN_EXPIRES_MINUTES}m)`);

    // In development or test environments, attach reset token for verification
    if (config.NODE_ENV !== 'production') {
      return {
        ...genericResponse,
        debug_token: rawResetToken,
        expiresAt: expiresAt.toISOString()
      };
    }

    return genericResponse;
  }

  /**
   * Reset Password
   * Validates token hash, updates password, revokes ALL existing refresh tokens
   */
  static async resetPassword(rawToken, newPassword) {
    if (!rawToken || typeof rawToken !== 'string') {
      throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'Valid reset token is required', 'TOKEN_REQUIRED');
    }

    const tokenHash = PasswordUtils.hashToken(rawToken);
    const user = await Storage.findUserByResetToken(tokenHash, true);

    if (!user) {
      throw new ApiError(
        HTTP_STATUS.BAD_REQUEST,
        'Invalid or expired password reset token. Please request a new one.',
        'INVALID_RESET_TOKEN'
      );
    }

    // Hash new password with bcrypt (12 rounds)
    const passwordHash = await PasswordUtils.hashPassword(newPassword);

    // Update user: set new password, clear reset token, REVOKE ALL SESSIONS for security
    await Storage.updateUser(user.userId, {
      passwordHash,
      resetPasswordToken: null,
      resetPasswordExpires: null,
      refreshTokens: [] // Immediately invalidates any compromised device or existing session!
    });

    logger.info(`Password successfully reset for user ${user.userId}. All active sessions invalidated.`);

    return {
      message: 'Password has been successfully reset. Please log in with your new password.'
    };
  }

  /**
   * User Logout
   * Revokes the specified refresh token
   */
  static async logout(userId, rawRefreshToken) {
    const user = await Storage.findUserById(userId, true);
    if (!user) return { message: 'Logged out successfully' };

    if (rawRefreshToken) {
      const tokenHash = PasswordUtils.hashToken(rawRefreshToken);
      const remainingTokens = (user.refreshTokens || []).filter((t) => t.tokenHash !== tokenHash);
      await Storage.updateUser(userId, { refreshTokens: remainingTokens });
    } else {
      // Clear all sessions if no specific token provided
      await Storage.updateUser(userId, { refreshTokens: [] });
    }

    return { message: 'Logged out successfully' };
  }

  /**
   * Validate Access Token (Used by gRPC & API Gateway)
   */
  static async validateToken(token) {
    if (!token) {
      return { isValid: false, errorMessage: 'Token not provided' };
    }

    const decoded = TokenUtils.verifyAccessToken(token);
    if (!decoded) {
      return { isValid: false, errorMessage: 'Token is invalid or expired' };
    }

    // Fast user & tenant status verification
    const user = await Storage.findUserById(decoded.userId);
    if (!user || user.status !== AUTH_CONSTANTS.USER_STATUS.ACTIVE) {
      return { isValid: false, errorMessage: 'User account is inactive or not found' };
    }

    return {
      isValid: true,
      userId: user.userId,
      tenantId: user.tenantId,
      email: user.email,
      roles: Array.isArray(user.role) ? user.role : [user.role]
    };
  }

  /**
   * Retrieve Current User Profile
   */
  static async getMe(userId) {
    const user = await Storage.findUserById(userId);
    if (!user) {
      throw new ApiError(HTTP_STATUS.NOT_FOUND, 'User profile not found', 'USER_NOT_FOUND');
    }

    const tenant = await TenantService.getTenantById(user.tenantId);
    return {
      user,
      tenant: {
        tenantId: tenant.tenantId,
        name: tenant.name,
        slug: tenant.slug,
        plan: tenant.plan,
        status: tenant.status
      }
    };
  }

  /**
   * Multi-Tenant: List Members within caller's tenant boundary
   */
  static async getTenantMembers(tenantId) {
    return Storage.findUsersByTenant(tenantId);
  }

  /**
   * Multi-Tenant: Add member to caller's tenant
   */
  static async addTenantMember(callerUserId, tenantId, { email, name, password, role }) {
    const caller = await Storage.findUserById(callerUserId);
    if (!caller || caller.role !== AUTH_CONSTANTS.ROLES.TENANT_ADMIN) {
      throw new ApiError(HTTP_STATUS.FORBIDDEN, 'Only tenant administrators can invite members', 'FORBIDDEN');
    }

    if (caller.tenantId !== tenantId) {
      throw new ApiError(HTTP_STATUS.FORBIDDEN, 'Cannot manage members for a different tenant workspace', 'TENANT_VIOLATION');
    }

    const normalizedEmail = email.toLowerCase().trim();
    const existing = await Storage.findUserByEmail(normalizedEmail, tenantId);
    if (existing) {
      throw new ApiError(HTTP_STATUS.CONFLICT, 'User already exists in this tenant workspace', 'USER_EXISTS');
    }

    const passwordHash = await PasswordUtils.hashPassword(password);
    const userId = `usr_${uuidv4().replace(/-/g, '').slice(0, 16)}`;

    const user = await Storage.createUser({
      userId,
      tenantId,
      email: normalizedEmail,
      passwordHash,
      name: name.trim(),
      role: role || AUTH_CONSTANTS.ROLES.DEVELOPER,
      status: AUTH_CONSTANTS.USER_STATUS.ACTIVE
    });

    return Storage.sanitizeUser(user);
  }
}

module.exports = AuthService;
