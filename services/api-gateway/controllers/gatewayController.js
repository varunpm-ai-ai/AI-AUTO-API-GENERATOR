/**
 * Gateway Route Controller
 */
const proxyRoutingService = require('../services/proxyRoutingService');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiError = require('../utils/apiError');
const asyncHandler = require('../utils/asyncHandler');

const proxyRouteHandler = asyncHandler(async (req, res, next) => {
  const targetServiceUrl = await proxyRoutingService.resolveTargetUrl(req.originalUrl);

  if (!targetServiceUrl) {
    throw new ApiError(HTTP_STATUS.NOT_FOUND, `No registered downstream microservice for route: ${req.originalUrl}`, 'ROUTE_NOT_FOUND');
  }

  await proxyRoutingService.proxyRequest(req, res, targetServiceUrl);
});

const getGatewayInfo = asyncHandler(async (req, res) => {
  const info = {
    service: 'API Gateway',
    version: '1.0.0',
    status: 'ACTIVE',
    edge_capabilities: [
      'Authentication & Token Verification',
      'API Key Validation & Revocation',
      'Distributed Rate Limiting',
      'Request ID & Correlation ID Injection',
      'Trusted Context Propagation',
      'Error Normalisation',
      'Audit Access Logging'
    ],
    timestamp: new Date().toISOString()
  };

  return ApiResponse.success(res, 'API Gateway edge specification', info);
});

module.exports = {
  proxyRouteHandler,
  getGatewayInfo
};
