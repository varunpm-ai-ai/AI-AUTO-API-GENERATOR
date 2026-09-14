/**
 * API Key Controller
 */
const apiKeyService = require('../services/apiKeyService');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const RESPONSE_MESSAGES = require('../constants/responseMessages');
const ApiError = require('../utils/apiError');
const asyncHandler = require('../utils/asyncHandler');

const createKey = asyncHandler(async (req, res) => {
  const { name, scopes, rateLimitMax, expiresAt } = req.body;
  const ownerId = req.gatewayContext.userId || 'admin-user';

  if (!name) {
    throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'API key name is required', 'MISSING_NAME');
  }

  const result = await apiKeyService.createKey(name, ownerId, {
    tenantId: req.gatewayContext.tenantId,
    scopes,
    rateLimitMax,
    expiresAt
  });

  return ApiResponse.success(res, RESPONSE_MESSAGES.KEY_CREATED, result, HTTP_STATUS.CREATED);
});

const listKeys = asyncHandler(async (req, res) => {
  const ownerId = req.gatewayContext.userId || 'admin-user';
  const keys = await apiKeyService.listKeys(ownerId);
  return ApiResponse.success(res, RESPONSE_MESSAGES.FETCHED, keys);
});

const revokeKey = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const ownerId = req.gatewayContext.userId || 'admin-user';

  const revoked = await apiKeyService.revokeKey(id, ownerId);
  if (!revoked) {
    throw new ApiError(HTTP_STATUS.NOT_FOUND, 'API key not found or unauthorized', 'KEY_NOT_FOUND');
  }

  return ApiResponse.success(res, RESPONSE_MESSAGES.KEY_REVOKED, { id });
});

const verifyKeyStatus = asyncHandler(async (req, res) => {
  const rawKey = req.body.apiKey || req.headers['x-api-key'];
  if (!rawKey) {
    throw new ApiError(HTTP_STATUS.BAD_REQUEST, 'API key parameter required', 'MISSING_KEY');
  }

  const keyRecord = await apiKeyService.verifyKey(rawKey);
  if (!keyRecord) {
    throw new ApiError(HTTP_STATUS.UNAUTHORIZED, 'Invalid or revoked API key', 'INVALID_KEY');
  }

  return ApiResponse.success(res, RESPONSE_MESSAGES.KEY_VALID, {
    keyPrefix: keyRecord.keyPrefix,
    name: keyRecord.name,
    status: keyRecord.status,
    scopes: keyRecord.scopes,
    lastUsedAt: keyRecord.lastUsedAt
  });
});

module.exports = {
  createKey,
  listKeys,
  revokeKey,
  verifyKeyStatus
};
