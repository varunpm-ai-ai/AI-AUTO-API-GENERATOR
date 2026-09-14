/**
 * API Key Service Layer
 * Implements Section 4.3 of API Gateway Implementation Spec.
 */
const ApiKey = require('../models/ApiKey');
const { generateApiKey, hashApiKey } = require('../utils/keyGenerator');
const logger = require('../config/logger');

class ApiKeyService {
  /**
   * Creates a new API Key for an owner
   */
  async createKey(name, ownerId, options = {}) {
    const { rawKey, keyPrefix, keyHash } = generateApiKey();

    const apiKey = await ApiKey.create({
      keyPrefix,
      keyHash,
      name,
      ownerId,
      tenantId: options.tenantId || 'default-tenant',
      scopes: options.scopes || ['read', 'write'],
      rateLimitMax: options.rateLimitMax || 100,
      expiresAt: options.expiresAt || null
    });

    logger.info(`Generated new API Key: ${name} (Prefix: ${keyPrefix}) for Owner: ${ownerId}`);

    // Return the raw key ONLY ONCE upon creation
    return {
      id: apiKey._id.toString(),
      name: apiKey.name,
      rawKey,
      keyPrefix: apiKey.keyPrefix,
      scopes: apiKey.scopes,
      expiresAt: apiKey.expiresAt,
      createdAt: apiKey.createdAt
    };
  }

  /**
   * Verifies a raw API Key sent in request header.
   */
  async verifyKey(rawKey) {
    if (!rawKey || typeof rawKey !== 'string') return null;

    const keyHash = hashApiKey(rawKey);
    const keyRecord = await ApiKey.findOne({ keyHash });

    if (!keyRecord || !keyRecord.isValid()) {
      return null;
    }

    // Async update last used timestamp
    ApiKey.updateOne({ _id: keyRecord._id }, { $set: { lastUsedAt: new Date() } }).catch((err) => {
      logger.error('Failed to update lastUsedAt for API Key', { error: err.message });
    });

    return keyRecord;
  }

  /**
   * Revokes an API Key
   */
  async revokeKey(keyId, ownerId) {
    const keyRecord = await ApiKey.findOne({ _id: keyId, ownerId });
    if (!keyRecord) return null;

    keyRecord.status = 'REVOKED';
    await keyRecord.save();
    logger.info(`Revoked API Key: ${keyId}`);
    return keyRecord;
  }

  /**
   * Lists API Keys for an owner (hides secret hashes)
   */
  async listKeys(ownerId) {
    return ApiKey.find({ ownerId })
      .select('-keyHash')
      .sort({ createdAt: -1 });
  }
}

module.exports = new ApiKeyService();
