/**
 * Authentication Controller
 * Handles HTTP requests for signup, login, refresh, password reset, and profile
 */
const { z } = require('zod');
const AuthService = require('../services/authService');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');

// Input Validation Schemas
const signupSchema = z.object({
  body: z.object({
    email: z.string().email('Please provide a valid email address').trim().toLowerCase(),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters long')
      .regex(/[A-Za-z]/, 'Password must contain at least one letter')
      .regex(/[0-9]/, 'Password must contain at least one digit'),
    name: z.string().min(2, 'Name must be at least 2 characters long').trim(),
    tenantName: z.string().min(2).optional(),
    tenantSlug: z.string().regex(/^[a-z0-9-]+$/, 'Tenant slug must be alphanumeric with hyphens').optional()
  })
});

const loginSchema = z.object({
  body: z.object({
    email: z.string().email('Please provide a valid email address').trim().toLowerCase(),
    password: z.string().min(1, 'Password is required'),
    tenantSlug: z.string().optional()
  })
});

const refreshSchema = z.object({
  body: z.object({
    refreshToken: z.string().min(1, 'Refresh token is required')
  })
});

const forgotPasswordSchema = z.object({
  body: z.object({
    email: z.string().email('Please provide a valid email address').trim().toLowerCase()
  })
});

const resetPasswordSchema = z.object({
  body: z.object({
    token: z.string().min(1, 'Password reset token is required'),
    newPassword: z
      .string()
      .min(8, 'New password must be at least 8 characters long')
      .regex(/[A-Za-z]/, 'Password must contain at least one letter')
      .regex(/[0-9]/, 'Password must contain at least one digit')
  })
});

class AuthController {
  /**
   * POST /api/v1/auth/signup
   */
  static async signup(req, res, next) {
    try {
      const result = await AuthService.signup(req.body);
      return ApiResponse.success(res, 'Account created successfully', result, HTTP_STATUS.CREATED);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/login
   */
  static async login(req, res, next) {
    try {
      const result = await AuthService.login(req.body);
      return ApiResponse.success(res, 'Authentication successful', result, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/refresh
   */
  static async refresh(req, res, next) {
    try {
      const result = await AuthService.refreshToken(req.body.refreshToken);
      return ApiResponse.success(res, 'Token refreshed successfully', result, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/forgot-password
   */
  static async forgotPassword(req, res, next) {
    try {
      const result = await AuthService.requestPasswordReset(req.body.email);
      return ApiResponse.success(res, result.message, result, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/reset-password
   */
  static async resetPassword(req, res, next) {
    try {
      const result = await AuthService.resetPassword(req.body.token, req.body.newPassword);
      return ApiResponse.success(res, result.message, result, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /api/v1/auth/logout
   */
  static async logout(req, res, next) {
    try {
      const userId = req.user?.userId;
      const refreshToken = req.body?.refreshToken;
      const result = await AuthService.logout(userId, refreshToken);
      return ApiResponse.success(res, result.message, null, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }

  /**
   * GET /api/v1/auth/me
   */
  static async getMe(req, res, next) {
    try {
      const result = await AuthService.getMe(req.user.userId);
      return ApiResponse.success(res, 'User profile retrieved successfully', result, HTTP_STATUS.OK);
    } catch (error) {
      next(error);
    }
  }
}

module.exports = {
  AuthController,
  signupSchema,
  loginSchema,
  refreshSchema,
  forgotPasswordSchema,
  resetPasswordSchema
};
