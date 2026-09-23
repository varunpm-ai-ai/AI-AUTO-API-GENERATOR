/**
 * Discovery Controller Handlers
 */
const discoveryFacade = require('../services/discoveryFacade');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');
const ApiError = require('../utils/apiError');
const asyncHandler = require('../utils/asyncHandler');
const Source = require('../models/Source');
const CrawlJob = require('../models/CrawlJob');

const initiateDiscovery = asyncHandler(async (req, res) => {
  const { query, category } = req.body;

  if (!query || typeof query !== 'string') {
    throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'Query parameter is required', 'MISSING_QUERY');
  }

  const result = await discoveryFacade.discover(query, category, req.authContext);
  return ApiResponse.success(res, RESPONSE_MESSAGES.DISCOVERY_INITIATED, result, HTTP_STATUS.CREATED);
});

const getDiscovery = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const result = await discoveryFacade.getDiscoveryById(id);

  if (!result) {
    throw new ApiError(HTTP_STATUS.NOT_FOUND, `Discovery request not found for ID: ${id}`, 'DISCOVERY_NOT_FOUND');
  }

  return ApiResponse.success(res, RESPONSE_MESSAGES.DISCOVERY_FETCHED, result);
});

const getDiscoverySources = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const sources = await Source.find({ discoveryRequestId: id }).sort({ rankScore: -1 });
  return ApiResponse.success(res, RESPONSE_MESSAGES.SOURCES_FOUND, sources);
});

const getDiscoveryJobs = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const jobs = await CrawlJob.find({ discoveryRequestId: id }).sort({ createdAt: -1 });
  return ApiResponse.success(res, RESPONSE_MESSAGES.CRAWL_SCHEDULED, jobs);
});

module.exports = {
  initiateDiscovery,
  getDiscovery,
  getDiscoverySources,
  getDiscoveryJobs
};
