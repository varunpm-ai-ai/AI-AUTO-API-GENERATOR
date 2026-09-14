/**
 * Audit & Access Logging Service
 */
const mongoose = require('mongoose');
const RequestLog = require('../models/RequestLog');
const logger = require('../config/logger');

class AuditLogService {
  async logAccess(req, res, responseTimeMs) {
    const logData = {
      requestId: req.requestId || 'unknown',
      correlationId: req.correlationId || 'unknown',
      method: req.method,
      path: req.originalUrl,
      clientIp: req.ip || req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown',
      authMethod: req.gatewayContext?.authMethod || 'ANONYMOUS',
      userId: req.gatewayContext?.userId || null,
      apiKeyId: req.gatewayContext?.apiKeyId || null,
      statusCode: res.statusCode,
      responseTimeMs,
      userAgent: req.headers['user-agent'] || ''
    };

    // Structured stdout access log
    logger.info(`[${logData.method}] ${logData.path} - ${logData.statusCode} (${responseTimeMs}ms)`, {
      requestId: logData.requestId,
      authMethod: logData.authMethod
    });

    // Save to database asynchronously only if connected
    if (mongoose.connection.readyState === 1) {
      RequestLog.create(logData).catch((err) => {
        logger.error('Failed to save RequestLog entry to database:', { error: err.message });
      });
    }
  }
}

module.exports = new AuditLogService();
