/**
 * Transactional Outbox Event Schema & Model
 * Implements Section 3.6 of Discovery Service Spec.
 */
const mongoose = require('mongoose');

const outboxEventSchema = new mongoose.Schema(
  {
    aggregateId: {
      type: String,
      required: true,
      index: true
    },
    eventType: {
      type: String,
      required: true,
      default: 'DATASET_ACQUIRED'
    },
    payload: {
      type: mongoose.Schema.Types.Mixed,
      required: true
    },
    status: {
      type: String,
      enum: ['PENDING', 'PUBLISHED', 'FAILED'],
      default: 'PENDING',
      index: true
    },
    publishedAt: {
      type: Date,
      default: null
    }
  },
  {
    timestamps: true
  }
);

const OutboxEvent = mongoose.model('OutboxEvent', outboxEventSchema);

module.exports = OutboxEvent;
