/**
 * Standardized Response Messages for Discovery Service
 */
const RESPONSE_MESSAGES = Object.freeze({
  DISCOVERY_INITIATED: 'Dataset discovery plan initiated successfully',
  DISCOVERY_FETCHED: 'Discovery request details retrieved successfully',
  SOURCES_FOUND: 'Candidate sources identified and ranked successfully',
  CRAWL_SCHEDULED: 'Crawl job created and scheduled for execution',
  ACQUISITION_SUCCESS: 'Dataset successfully acquired and persisted to storage',
  
  BAD_REQUEST: 'Invalid dataset discovery parameters or body',
  NOT_FOUND: 'Discovery request or target dataset not found',
  AI_PLANNING_FAILED: 'Failed to generate valid discovery plan from AI provider',
  CRAWL_FAILED: 'Crawl command execution failed or timed out',
  INTERNAL_ERROR: 'An internal Discovery Service error occurred'
});

module.exports = RESPONSE_MESSAGES;
