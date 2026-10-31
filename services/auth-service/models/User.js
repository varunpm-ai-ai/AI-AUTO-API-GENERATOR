/**
 * User Entity Schema & Model
 * Enforces Role-Based Access Control and Password Security
 */
const mongoose = require('mongoose');
const AUTH_CONSTANTS = require('../constants/authConstants');

const refreshTokenSchema = new mongoose.Schema(
  {
    tokenId: { type: String, required: true },
    tokenHash: { type: String, required: true, index: true },
    expiresAt: { type: Date, required: true },
    createdAt: { type: Date, default: Date.now }
  },
  { _id: false }
);

const userSchema = new mongoose.Schema(
  {
    userId: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    tenantId: {
      type: String,
      required: true,
      index: true
    },
    email: {
      type: String,
      required: true,
      lowercase: true,
      trim: true,
      index: true
    },
    passwordHash: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true,
      trim: true
    },
    role: {
      type: String,
      enum: Object.values(AUTH_CONSTANTS.ROLES),
      default: AUTH_CONSTANTS.ROLES.VIEWER,
      index: true
    },
    status: {
      type: String,
      enum: Object.values(AUTH_CONSTANTS.USER_STATUS),
      default: AUTH_CONSTANTS.USER_STATUS.ACTIVE,
      index: true
    },
    resetPasswordToken: {
      type: String,
      default: null,
      index: true
    },
    resetPasswordExpires: {
      type: Date,
      default: null
    },
    refreshTokens: [refreshTokenSchema]
  },
  {
    timestamps: true,
    toJSON: {
      virtuals: true,
      transform: (doc, ret) => {
        delete ret.passwordHash;
        delete ret.resetPasswordToken;
        delete ret.resetPasswordExpires;
        delete ret.refreshTokens;
        delete ret.__v;
        return ret;
      }
    }
  }
);

// Compound index to ensure uniqueness of email within each tenant (or globally)
userSchema.index({ email: 1, tenantId: 1 }, { unique: true });

const User = mongoose.model('User', userSchema);

module.exports = User;
