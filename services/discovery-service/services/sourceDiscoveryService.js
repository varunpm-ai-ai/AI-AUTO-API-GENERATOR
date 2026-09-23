/**
 * Source Processing Pipeline Service
 * Implements Section 4.4 of Discovery Service Spec.
 */
const mongoose = require('mongoose');
const Source = require('../models/Source');
const logger = require('../config/logger');

class SourceDiscoveryService {
  async processSources(discoveryRequest, discoveryPlan) {
    const candidateUrls = discoveryPlan.targetDomains.map(
      (domain) => `https://${domain}/api/v1/datasets?query=${encodeURIComponent(discoveryRequest.query)}`
    );

    const processedSources = [];
    const isDbConnected = mongoose.connection.readyState === 1;

    for (const url of candidateUrls) {
      const domain = new URL(url).hostname;
      const isValid = this.validateSourceUrl(url);
      const classification = this.classifySource(url, domain);
      const rankScore = this.rankSource(classification, domain);

      const sourceRecord = isDbConnected
        ? await Source.create({
            discoveryRequestId: discoveryRequest._id,
            url,
            domain,
            classification,
            isValid,
            rankScore
          })
        : {
            _id: new mongoose.Types.ObjectId(),
            discoveryRequestId: discoveryRequest._id,
            url,
            domain,
            classification,
            isValid,
            rankScore
          };

      processedSources.push(sourceRecord);
    }

    processedSources.sort((a, b) => b.rankScore - a.rankScore);
    logger.info(`Processed ${processedSources.length} candidate sources for Request: ${discoveryRequest._id}`);
    return processedSources;
  }

  validateSourceUrl(url) {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  }

  classifySource(url, domain) {
    if (domain.includes('gov')) return 'GOVERNMENT';
    if (url.includes('/api/')) return 'API_ENDPOINT';
    if (domain.includes('github') || domain.includes('kaggle')) return 'OPEN_DATA';
    return 'HTML_PAGE';
  }

  rankSource(classification, domain) {
    switch (classification) {
      case 'GOVERNMENT':
        return 0.95;
      case 'API_ENDPOINT':
        return 0.9;
      case 'OPEN_DATA':
        return 0.85;
      default:
        return 0.7;
    }
  }
}

module.exports = new SourceDiscoveryService();
