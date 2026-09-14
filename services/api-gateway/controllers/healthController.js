/**
 * Health & Readiness Check Controller
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
    service: 'api-gateway',
    status: 'UP',
    uptimeSeconds: process.uptime(),
    timestamp: new Date().toISOString(),
    database: {
      status: dbStatusMap[dbState] || 'UNKNOWN',
      connected: dbState === 1
    },
    memoryUsage: process.memoryUsage()
  };

  return ApiResponse.success(res, 'API Gateway is healthy', healthData);
});

const getReadiness = asyncHandler(async (req, res) => {
  // Liveness/Readiness check
  const isDbReady = mongoose.connection.readyState === 1;

  if (!isDbReady) {
    // In dev mode, still report UP if DB not strictly enforced
    const readinessData = {
      ready: false,
      reason: 'Database connection not ready'
    };
    return ApiResponse.error(res, HTTP_STATUS.SERVICE_UNAVAILABLE, 'Service Not Ready', 'NOT_READY', readinessData);
  }

  return ApiResponse.success(res, 'API Gateway is ready to accept traffic', { ready: true });
});

module.exports = {
  getHealth,
  getReadiness
};
