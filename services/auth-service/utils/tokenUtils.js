/**
 * Token Management Utilities (JWT & Refresh Tokens)
 */
const jwt = require('jsonwebtoken');
const config = require('../config/env');
const PasswordUtils = require('./passwordUtils');
const AUTH_CONSTANTS = require('../constants/authConstants');

class TokenUtils {
  /**
   * Generates a signed JWT Access Token
   */
  static generateAccessToken(user) {
    const payload = {
      sub: user.userId,
      userId: user.userId,
      tenantId: user.tenantId,
      email: user.email,
      roles: Array.isArray(user.role) ? user.role : [user.role || AUTH_CONSTANTS.ROLES.VIEWER],
      name: user.name
    };

    return jwt.sign(payload, config.JWT_SECRET, {
      expiresIn: config.JWT_EXPIRES_IN,
      algorithm: 'HS256'
    });
  }

  /**
   * Generates a secure raw refresh token and its SHA-256 hash
   */
  static generateRefreshToken() {
    const rawToken = PasswordUtils.generateRandomToken(AUTH_CONSTANTS.REFRESH_TOKEN_BYTES);
    const tokenHash = PasswordUtils.hashToken(rawToken);
    const expiresAt = new Date(Date.now() + config.REFRESH_TOKEN_EXPIRES_DAYS * 24 * 60 * 60 * 1000);

    return {
      rawToken,
      tokenHash,
      expiresAt
    };
  }

  /**
   * Verifies and decodes a JWT access token
   */
  static verifyAccessToken(token) {
    try {
      return jwt.verify(token, config.JWT_SECRET, { algorithms: ['HS256'] });
    } catch (err) {
      return null;
    }
  }

  /**
   * Safely decodes a JWT token without verification
   */
  static decodeToken(token) {
    return jwt.decode(token);
  }
}

module.exports = TokenUtils;
