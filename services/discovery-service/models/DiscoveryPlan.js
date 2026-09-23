/**
 * Discovery Plan Schema & Model
 * Structured AI-generated plan.
 */
const mongoose = require('mongoose');

const discoveryPlanSchema = new mongoose.Schema(
  {
    discoveryRequestId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DiscoveryRequest',
      required: true,
      index: true
    },
    targetDomains: {
      type: [String],
      default: []
    },
    searchQueries: {
      type: [String],
      default: []
    },
    expectedFormats: {
      type: [String],
      default: ['json', 'csv']
    },
    recommendedCrawler: {
      type: String,
      default: 'HTTP_CRAWLER'
    },
    confidenceScore: {
      type: Number,
      default: 0.95
    },
    validated: {
      type: Boolean,
      default: true
    }
  },
  {
    timestamps: true
  }
);

const DiscoveryPlan = mongoose.model('DiscoveryPlan', discoveryPlanSchema);

module.exports = DiscoveryPlan;
