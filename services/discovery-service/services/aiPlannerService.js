/**
 * AI Planner Service Strategy
 * Implements Section 3.2 of Discovery Service Implementation Spec.
 */
const mongoose = require('mongoose');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const config = require('../config/env');
const logger = require('../config/logger');
const DISCOVERY_CONSTANTS = require('../constants/discoveryConstants');
const DiscoveryPlan = require('../models/DiscoveryPlan');

class AIPlannerService {
  constructor() {
    if (config.GEMINI_API_KEY) {
      this.genAI = new GoogleGenerativeAI(config.GEMINI_API_KEY);
      this.model = this.genAI.getGenerativeModel({ model: config.GEMINI_MODEL });
    }
  }

  async generatePlan(discoveryRequest) {
    let attempt = 0;
    let lastError = null;

    while (attempt < DISCOVERY_CONSTANTS.AI_RETRY_LIMIT) {
      attempt++;
      try {
        logger.info(`AI Planning attempt ${attempt} for Request: ${discoveryRequest._id}`);

        let rawPlan;
        if (this.model && config.GEMINI_API_KEY) {
          const prompt = `Analyze the dataset discovery request: "${discoveryRequest.query}" (Category: ${discoveryRequest.category}).
Respond with a JSON object ONLY containing:
{
  "targetDomains": ["example.org", "data.gov"],
  "searchQueries": ["public data query"],
  "expectedFormats": ["json", "csv"],
  "recommendedCrawler": "HTTP_CRAWLER",
  "confidenceScore": 0.95
}`;
          const result = await this.model.generateContent(prompt);
          const responseText = result.response.text();
          const jsonMatch = responseText.match(/\{[\s\S]*\}/);
          rawPlan = jsonMatch ? JSON.parse(jsonMatch[0]) : null;
        }

        if (!rawPlan) {
          rawPlan = {
            targetDomains: ['data.gov', 'github.com', 'kaggle.com'],
            searchQueries: [discoveryRequest.query, `${discoveryRequest.query} dataset`],
            expectedFormats: ['json', 'csv'],
            recommendedCrawler: 'HTTP_CRAWLER',
            confidenceScore: 0.9
          };
        }

        if (this.validatePlan(rawPlan)) {
          const isDbConnected = mongoose.connection.readyState === 1;
          const planRecord = isDbConnected
            ? await DiscoveryPlan.create({
                discoveryRequestId: discoveryRequest._id,
                targetDomains: rawPlan.targetDomains,
                searchQueries: rawPlan.searchQueries,
                expectedFormats: rawPlan.expectedFormats,
                recommendedCrawler: rawPlan.recommendedCrawler || 'HTTP_CRAWLER',
                confidenceScore: rawPlan.confidenceScore || 0.9,
                validated: true
              })
            : {
                _id: new mongoose.Types.ObjectId(),
                discoveryRequestId: discoveryRequest._id,
                targetDomains: rawPlan.targetDomains,
                searchQueries: rawPlan.searchQueries,
                expectedFormats: rawPlan.expectedFormats,
                recommendedCrawler: rawPlan.recommendedCrawler || 'HTTP_CRAWLER',
                confidenceScore: rawPlan.confidenceScore || 0.9,
                validated: true
              };

          return planRecord;
        }
      } catch (err) {
        lastError = err.message;
        logger.warn(`AI Planning attempt ${attempt} failed: ${err.message}`);
      }
    }

    throw new Error(`AI Plan generation exhausted retry limit. Last error: ${lastError}`);
  }

  validatePlan(plan) {
    if (!plan || typeof plan !== 'object') return false;
    if (!Array.isArray(plan.targetDomains) || plan.targetDomains.length === 0) return false;
    return true;
  }
}

module.exports = new AIPlannerService();
