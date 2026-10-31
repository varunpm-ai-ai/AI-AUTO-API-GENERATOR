/**
 * Cryptographic & Password Security Utilities
 * Prevents timing attacks, leaks, and insecure hashes
 */
const crypto = require('crypto');
const bcrypt = require('bcryptjs');
const AUTH_CONSTANTS = require('../constants/authConstants');

class PasswordUtils {
  /**
   * Hashes a password using bcrypt with 12 salt rounds
   */
  static async hashPassword(password) {
    return bcrypt.hash(password, AUTH_CONSTANTS.BCRYPT_SALT_ROUNDS);
  }

  /**
   * Verifies plaintext password against stored bcrypt hash (constant-time)
   */
  static async verifyPassword(plainPassword, passwordHash) {
    if (!plainPassword || !passwordHash) return false;
    return bcrypt.compare(plainPassword, passwordHash);
  }

  /**
   * Generates a cryptographically strong random token
   */
  static generateRandomToken(bytes = AUTH_CONSTANTS.RESET_TOKEN_BYTES) {
    return crypto.randomBytes(bytes).toString('hex');
  }

  /**
   * Computes SHA-256 digest of a token before saving in database.
   * This guarantees that even if the database is dumped, raw reset tokens are never exposed.
   */
  static hashToken(token) {
    if (!token) return '';
    return crypto.createHash('sha256').update(String(token)).digest('hex');
  }

  /**
   * Constant-time string comparison to defend against timing attacks
   */
  static safeCompare(a, b) {
    if (typeof a !== 'string' || typeof b !== 'string') return false;
    const bufA = Buffer.from(a);
    const bufB = Buffer.from(b);
    if (bufA.length !== bufB.length) return false;
    return crypto.timingSafeEqual(bufA, bufB);
  }
}

module.exports = PasswordUtils;
