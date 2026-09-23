/**
 * Crawl Job Scheduler & Command Execution Service
 * Implements Section 3.7 & 4.5 of Discovery Service Spec.
 */
const mongoose = require('mongoose');
const CrawlJob = require('../models/CrawlJob');
const logger = require('../config/logger');
const acquisitionService = require('./acquisitionService');

class CrawlSchedulerService {
  async scheduleCrawlJob(discoveryRequest, topSource, recommendedCrawler = 'HTTP_CRAWLER') {
    const isDbConnected = mongoose.connection.readyState === 1;
    const job = isDbConnected
      ? await CrawlJob.create({
          discoveryRequestId: discoveryRequest._id,
          sourceId: topSource._id,
          sourceUrl: topSource.url,
          crawlerType: recommendedCrawler,
          status: 'SCHEDULED'
        })
      : {
          _id: new mongoose.Types.ObjectId(),
          discoveryRequestId: discoveryRequest._id,
          sourceId: topSource._id,
          sourceUrl: topSource.url,
          crawlerType: recommendedCrawler,
          status: 'SCHEDULED',
          save: async function () { return this; }
        };

    logger.info(`Scheduled Crawl Job ${job._id} (Crawler: ${recommendedCrawler}) for Source: ${topSource.url}`);
    return this.executeCrawlCommand(job, discoveryRequest);
  }

  async executeCrawlCommand(crawlJob, discoveryRequest) {
    crawlJob.status = 'RUNNING';
    await crawlJob.save();

    try {
      const acquiredDataset = await acquisitionService.acquire(discoveryRequest, crawlJob);
      crawlJob.status = 'COMPLETED';
      await crawlJob.save();
      return acquiredDataset;
    } catch (error) {
      crawlJob.retryCount = (crawlJob.retryCount || 0) + 1;
      crawlJob.errorMessage = error.message;
      crawlJob.status = crawlJob.retryCount >= (crawlJob.maxRetries || 3) ? 'FAILED' : 'SCHEDULED';
      await crawlJob.save();
      throw error;
    }
  }
}

module.exports = new CrawlSchedulerService();
