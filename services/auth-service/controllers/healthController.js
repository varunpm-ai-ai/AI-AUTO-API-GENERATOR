/**
 * Health & Readiness Controller for Auth Service
 */
const config = require('../config/env');
const { getDbStatus } = require('../config/db');
const ApiResponse = require('../utils/apiResponse');
const HTTP_STATUS = require('../constants/httpStatusCodes');

class HealthController {
  static getHealth(req, res) {
    return ApiResponse.success(res, 'Auth Service is healthy', {
      status: 'UP',
      service: 'auth-service',
      environment: config.NODE_ENV,
      port: config.PORT,
      grpc_port: config.GRPC_PORT,
      uptime: process.uptime()
    }, HTTP_STATUS.OK);
  }

  static getReadiness(req, res) {
    const isDbConnected = getDbStatus();
    return ApiResponse.success(res, 'Auth Service readiness check passed', {
      status: 'READY',
      service: 'auth-service',
      database: isDbConnected ? 'CONNECTED' : 'IN_MEMORY_FALLBACK',
      grpc: 'ACTIVE'
    }, HTTP_STATUS.OK);
  }
}

module.exports = HealthController;
