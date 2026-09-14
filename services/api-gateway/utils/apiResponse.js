/**
 * Standardized API Response Formatter for API Gateway
 */
const HTTP_STATUS = require('../constants/httpStatusCodes');

class ApiResponse {
  static success(res, message, data = null, statusCode = HTTP_STATUS.OK, meta = {}) {
    const requestId = res.req ? (res.req.requestId || res.req.headers['x-request-id']) : undefined;
    return res.status(statusCode).json({
      success: true,
      message,
      data,
      meta: {
        request_id: requestId,
        timestamp: new Date().toISOString(),
        ...meta
      }
    });
  }

  static error(res, statusCode, message, errorCode = 'API_GATEWAY_ERROR', details = null, requestId = null) {
    return res.status(statusCode).json({
      success: false,
      error: {
        code: errorCode,
        message,
        details,
        request_id: requestId || (res.req ? (res.req.requestId || res.req.headers['x-request-id']) : null),
        timestamp: new Date().toISOString()
      }
    });
  }
}

module.exports = ApiResponse;
