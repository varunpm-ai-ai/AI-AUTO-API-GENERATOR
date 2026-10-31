/**
 * Authentication Endpoints Route Registry
 */
const express = require('express');
const router = express.Router();

const {
  AuthController,
  signupSchema,
  loginSchema,
  refreshSchema,
  forgotPasswordSchema,
  resetPasswordSchema
} = require('../controllers/authController');

const validateRequest = require('../middlewares/validateRequest');
const { authenticate, requireAuth } = require('../middlewares/authMiddleware');
const { authStrictLimiter } = require('../middlewares/rateLimiter');

// Public authentication flows (rate limited against brute-force)
router.post('/signup', authStrictLimiter, validateRequest(signupSchema), AuthController.signup);
router.post('/login', authStrictLimiter, validateRequest(loginSchema), AuthController.login);
router.post('/refresh', validateRequest(refreshSchema), AuthController.refresh);
router.post('/forgot-password', authStrictLimiter, validateRequest(forgotPasswordSchema), AuthController.forgotPassword);
router.post('/reset-password', authStrictLimiter, validateRequest(resetPasswordSchema), AuthController.resetPassword);

// Authenticated user endpoints
router.post('/logout', authenticate, AuthController.logout);
router.get('/me', authenticate, requireAuth, AuthController.getMe);

module.exports = router;
