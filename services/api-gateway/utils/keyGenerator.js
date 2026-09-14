/**
 * Secure Crypto Key Generator & Hasher for API Keys
 */
const crypto = require('crypto');
const API_CONSTANTS = require('../constants/apiConstants');
const config = require('../config/env');

/**
 * Generates a raw API key and its hashed version.
 * Raw Key format: ak_<32 random hex bytes>
 */
const generateApiKey = () => {
  const randomBytes = crypto.randomBytes(24).toString('hex');
  const rawKey = `${API_CONSTANTS.API_KEY_PREFIX}${randomBytes}`;
  const keyPrefix = rawKey.substring(0, 7); // e.g. ak_1234
  const keyHash = hashApiKey(rawKey);

  return { rawKey, keyPrefix, keyHash };
};

/**
 * Hashes an API key using SHA-256 with configured salt.
 */
const hashApiKey = (rawKey) => {
  return crypto
    .createHmac('sha256', config.API_KEY_SALT)
    .update(rawKey)
    .digest('hex');
};

module.exports = {
  generateApiKey,
  hashApiKey
};
