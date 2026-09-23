/**
 * Acquired Dataset Schema & Model
 * Raw dataset metadata source of truth.
 */
const mongoose = require('mongoose');

const acquiredDatasetSchema = new mongoose.Schema(
  {
    discoveryRequestId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DiscoveryRequest',
      required: true,
      index: true
    },
    storageKey: {
      type: String,
      required: true,
      unique: true
    },
    storageUri: {
      type: String,
      required: true
    },
    sourceUrl: {
      type: String,
      required: true
    },
    checksum: {
      type: String,
      required: true
    },
    contentType: {
      type: String,
      default: 'application/json'
    },
    fileSizeBytes: {
      type: Number,
      default: 0
    },
    metadata: {
      type: mongoose.Schema.Types.Mixed,
      default: {}
    }
  },
  {
    timestamps: true
  }
);

const AcquiredDataset = mongoose.model('AcquiredDataset', acquiredDatasetSchema);

module.exports = AcquiredDataset;
