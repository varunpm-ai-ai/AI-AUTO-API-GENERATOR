/**
 * Tenant Entity Schema & Model
 * Enforces Multi-Tenant Boundary Isolation
 */
const mongoose = require('mongoose');
const AUTH_CONSTANTS = require('../constants/authConstants');

const tenantSchema = new mongoose.Schema(
  {
    tenantId: {
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
    slug: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      index: true
    },
    plan: {
      type: String,
      enum: ['starter', 'pro', 'enterprise'],
      default: 'starter'
    },
    status: {
      type: String,
      enum: Object.values(AUTH_CONSTANTS.TENANT_STATUS),
      default: AUTH_CONSTANTS.TENANT_STATUS.ACTIVE,
      index: true
    },
    settings: {
      maxUsers: { type: Number, default: 50 },
      allowedDomains: [{ type: String }],
      requireMFA: { type: Boolean, default: false }
    }
  },
  {
    timestamps: true,
    toJSON: {
      virtuals: true,
      transform: (doc, ret) => {
        delete ret.__v;
        return ret;
      }
    }
  }
);

const Tenant = mongoose.model('Tenant', tenantSchema);

module.exports = Tenant;
