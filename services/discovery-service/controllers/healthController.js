/**
 * Health Check Controller for Discovery Service
 */
const mongoose = require('mongoose');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const asyncHandler = require('../utils/asyncHandler');

const getHealth = asyncHandler(async (req, res) => {
  const dbState = mongoose.connection.readyState;
  const dbStatusMap = {
    0: 'DISCONNECTED',
    1: 'CONNECTED',
    2: 'CONNECTING',
    3: 'DISCONNECTING'
  };

  const healthData = {
    service: 'discovery-service',
    status: 'UP',
    uptimeSeconds: process.uptime(),
    timestamp: new Date().toISOString(),
    database: {
      status: dbStatusMap[dbState] || 'UNKNOWN',
      connected: dbState === 1
    }
  };

  return ApiResponse.success(res, 'Discovery Service is healthy', healthData);
});

const getReadiness = asyncHandler(async (req, res) => {
  const isDbReady = mongoose.connection.readyState === 1;

  if (!isDbReady) {
    return ApiResponse.error(res, HTTP_STATUS.SERVICE_UNAVAILABLE, 'Service Not Ready', 'NOT_READY', { ready: false });
  }

  return ApiResponse.success(res, 'Discovery Service is ready', { ready: true });
});

module.exports = {
  getHealth,
  getReadiness
};
