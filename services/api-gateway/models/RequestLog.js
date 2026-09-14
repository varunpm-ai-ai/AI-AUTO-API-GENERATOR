/**
 * Request Access & Audit Log Schema & Model
 */
const mongoose = require('mongoose');

const requestLogSchema = new mongoose.Schema(
  {
    requestId: {
      type: String,
      required: true,
      index: true
    },
    correlationId: {
      type: String,
      required: true,
      index: true
    },
    method: {
      type: String,
      required: true
    },
    path: {
      type: String,
      required: true
    },
    clientIp: {
      type: String,
      default: 'unknown'
    },
    authMethod: {
      type: String,
      default: 'ANONYMOUS'
    },
    userId: {
      type: String,
      default: null
    },
    apiKeyId: {
      type: String,
      default: null
    },
    statusCode: {
      type: Number,
      required: true
    },
    responseTimeMs: {
      type: Number,
      required: true
    },
    userAgent: {
      type: String,
      default: ''
    }
  },
  {
    timestamps: true
  }
);

requestLogSchema.index({ createdAt: -1 });

const RequestLog = mongoose.model('RequestLog', requestLogSchema);

module.exports = RequestLog;
