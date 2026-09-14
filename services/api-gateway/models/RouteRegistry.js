/**
 * Dynamic Gateway Route Registry Model
 * Defines downstream microservice mappings.
 */
const mongoose = require('mongoose');

const routeRegistrySchema = new mongoose.Schema(
  {
    pathPattern: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    targetService: {
      type: String,
      required: true
    },
    targetUrl: {
      type: String,
      required: true
    },
    authRequired: {
      type: Boolean,
      default: false
    },
    requiredScopes: {
      type: [String],
      default: []
    },
    rateLimitMax: {
      type: Number,
      default: 100
    },
    isActive: {
      type: Boolean,
      default: true
    }
  },
  {
    timestamps: true
  }
);

const RouteRegistry = mongoose.model('RouteRegistry', routeRegistrySchema);

module.exports = RouteRegistry;
