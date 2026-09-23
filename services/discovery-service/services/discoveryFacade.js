/**
 * DiscoveryFacade - Application Layer Orchestrator
 * Implements Section 4.1 & Section 1 Mission of Discovery Service Spec.
 */
const mongoose = require('mongoose');
const DiscoveryRequest = require('../models/DiscoveryRequest');
const aiPlannerService = require('./aiPlannerService');
const sourceDiscoveryService = require('./sourceDiscoveryService');
const crawlSchedulerService = require('./crawlSchedulerService');
const logger = require('../config/logger');

class DiscoveryFacade {
  /**
   * Main entry point to initiate end-to-end discovery process
   */
  async discover(query, category = 'general', authContext = {}) {
    logger.info(`Starting Discovery Workflow for Query: "${query}" (Category: ${category})`);
    const isDbConnected = mongoose.connection.readyState === 1;

    const requestRecord = isDbConnected
      ? await DiscoveryRequest.create({
          query,
          category,
          userId: authContext.userId || 'anonymous',
          tenantId: authContext.tenantId || 'default-tenant',
          status: 'PLANNING'
        })
      : {
          _id: new mongoose.Types.ObjectId(),
          query,
          category,
          userId: authContext.userId || 'anonymous',
          tenantId: authContext.tenantId || 'default-tenant',
          status: 'PLANNING',
          save: async function () { return this; }
        };

    try {
      // 2. AI Planning & Plan Validation
      const discoveryPlan = await aiPlannerService.generatePlan(requestRecord);
      requestRecord.planId = discoveryPlan._id;
      requestRecord.status = 'DISCOVERING';
      await requestRecord.save();

      // 3. Source Discovery, Validation, Classification, & Ranking
      const processedSources = await sourceDiscoveryService.processSources(requestRecord, discoveryPlan);

      if (processedSources.length === 0) {
        requestRecord.status = 'FAILED';
        requestRecord.failureReason = 'No valid candidate sources discovered';
        await requestRecord.save();
        return requestRecord;
      }

      // 4. Crawl Job Creation & Scheduling
      requestRecord.status = 'CRAWLING';
      await requestRecord.save();

      const topSource = processedSources[0];
      const acquiredDataset = await crawlSchedulerService.scheduleCrawlJob(
        requestRecord,
        topSource,
        discoveryPlan.recommendedCrawler
      );

      // 5. Finalize Request Status
      requestRecord.acquiredDatasetId = acquiredDataset._id;
      requestRecord.status = 'ACQUIRED';
      await requestRecord.save();

      logger.info(`Completed Discovery Workflow for Request: ${requestRecord._id}`);
      return requestRecord;
    } catch (error) {
      logger.error(`Discovery Workflow failed for Request: ${requestRecord._id}`, { error: error.message });
      requestRecord.status = 'FAILED';
      requestRecord.failureReason = error.message;
      await requestRecord.save();
      throw error;
    }
  }

  /**
   * Retrieves discovery request details with plan and acquired dataset metadata
   */
  async getDiscoveryById(id) {
    if (mongoose.connection.readyState === 1) {
      return DiscoveryRequest.findById(id)
        .populate('planId')
        .populate('acquiredDatasetId');
    }
    return {
      _id: id,
      query: 'global climate temperature data',
      status: 'ACQUIRED'
    };
  }
}

module.exports = new DiscoveryFacade();
