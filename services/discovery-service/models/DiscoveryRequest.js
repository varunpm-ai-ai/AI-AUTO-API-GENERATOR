/**
 * Discovery Request Schema & Model
 * Implements Section 7.1 of Discovery Service Implementation Spec.
 */
const mongoose = require('mongoose');

const discoveryRequestSchema = new mongoose.Schema(
  {
    query: {
      type: String,
      required: true,
      trim: true
    },
    category: {
      type: String,
      default: 'general'
    },
    userId: {
      type: String,
      default: 'anonymous'
    },
    tenantId: {
      type: String,
      default: 'default-tenant'
    },
    status: {
      type: String,
      enum: ['PENDING', 'PLANNING', 'DISCOVERING', 'CRAWLING', 'ACQUIRED', 'FAILED'],
      default: 'PENDING',
      index: true
    },
    planId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DiscoveryPlan',
      default: null
    },
    acquiredDatasetId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'AcquiredDataset',
      default: null
    },
    failureReason: {
      type: String,
      default: null
    }
  },
  {
    timestamps: true
  }
);

const DiscoveryRequest = mongoose.model('DiscoveryRequest', discoveryRequestSchema);

module.exports = DiscoveryRequest;
