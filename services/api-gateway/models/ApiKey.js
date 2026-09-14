/**
 * API Key Mongoose Schema & Model
 * Implements section 4.3 of API Gateway Implementation Spec.
 */
const mongoose = require('mongoose');

const apiKeySchema = new mongoose.Schema(
  {
    keyPrefix: {
      type: String,
      required: true,
      index: true
    },
    keyHash: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    name: {
      type: String,
      required: true,
      trim: true
    },
    ownerId: {
      type: String,
      required: true,
      index: true
    },
    tenantId: {
      type: String,
      default: 'default-tenant'
    },
    status: {
      type: String,
      enum: ['ACTIVE', 'REVOKED', 'EXPIRED'],
      default: 'ACTIVE',
      index: true
    },
    scopes: {
      type: [String],
      default: ['read', 'write']
    },
    rateLimitMax: {
      type: Number,
      default: 100
    },
    expiresAt: {
      type: Date,
      default: null
    },
    lastUsedAt: {
      type: Date,
      default: null
    }
  },
  {
    timestamps: true
  }
);

// Helper method to check validity
apiKeySchema.methods.isValid = function () {
  if (this.status !== 'ACTIVE') return false;
  if (this.expiresAt && new Date() > this.expiresAt) return false;
  return true;
};

const ApiKey = mongoose.model('ApiKey', apiKeySchema);

module.exports = ApiKey;
