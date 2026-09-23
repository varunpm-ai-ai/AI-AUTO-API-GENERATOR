/**
 * Crawl Job & Command Schema & Model
 * Implements Section 4.5 of Discovery Service Spec.
 */
const mongoose = require('mongoose');

const crawlJobSchema = new mongoose.Schema(
  {
    discoveryRequestId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DiscoveryRequest',
      required: true,
      index: true
    },
    sourceId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Source',
      required: true
    },
    sourceUrl: {
      type: String,
      required: true
    },
    crawlerType: {
      type: String,
      enum: ['HTTP_CRAWLER', 'API_CRAWLER', 'BROWSER_CRAWLER'],
      default: 'HTTP_CRAWLER'
    },
    status: {
      type: String,
      enum: ['SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED'],
      default: 'SCHEDULED',
      index: true
    },
    retryCount: {
      type: Number,
      default: 0
    },
    maxRetries: {
      type: Number,
      default: 3
    },
    errorMessage: {
      type: String,
      default: null
    }
  },
  {
    timestamps: true
  }
);

const CrawlJob = mongoose.model('CrawlJob', crawlJobSchema);

module.exports = CrawlJob;
