/**
 * Discovered Source Schema & Model
 */
const mongoose = require('mongoose');

const sourceSchema = new mongoose.Schema(
  {
    discoveryRequestId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DiscoveryRequest',
      required: true,
      index: true
    },
    url: {
      type: String,
      required: true
    },
    domain: {
      type: String,
      required: true
    },
    classification: {
      type: String,
      enum: ['GOVERNMENT', 'OPEN_DATA', 'API_ENDPOINT', 'HTML_PAGE', 'UNKNOWN'],
      default: 'OPEN_DATA'
    },
    isValid: {
      type: Boolean,
      default: true
    },
    rankScore: {
      type: Number,
      default: 0.8,
      index: true
    }
  },
  {
    timestamps: true
  }
);

const Source = mongoose.model('Source', sourceSchema);

module.exports = Source;
