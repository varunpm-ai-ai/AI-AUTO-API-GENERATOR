/**
 * Reverse Proxy & Dynamic Routing Engine for API Gateway
 * Implements Section 4.1 & Section 9 of API Gateway Implementation Spec.
 */
const http = require('http');
const https = require('https');
const { URL } = require('url');
const config = require('../config/env');
const logger = require('../config/logger');
const API_CONSTANTS = require('../constants/apiConstants');
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiError = require('../utils/apiError');
const RouteRegistry = require('../models/RouteRegistry');

class ProxyRoutingService {
  constructor() {
    // Default static downstream service mappings fallback
    this.defaultRoutes = [
      {
        pathPrefix: '/api/v1/discover',
        targetBaseUrl: config.DISCOVERY_SERVICE_URL
      },
      {
        pathPrefix: '/api/v1/workspace',
        targetBaseUrl: config.WORKSPACE_SERVICE_URL
      }
    ];
  }

  /**
   * Resolves target URL for an incoming request path.
   */
  async resolveTargetUrl(path) {
    // 1. Check dynamic DB route registry if connected
    try {
      const match = await RouteRegistry.findOne({ isActive: true, pathPattern: { $regex: `^${path}` } });
      if (match) {
        return match.targetUrl;
      }
    } catch (e) {
      // Fallback to static route mapping if DB check skipped
    }

    // 2. Fallback to default microservice route mappings
    for (const route of this.defaultRoutes) {
      if (path.startsWith(route.pathPrefix)) {
        return route.targetBaseUrl;
      }
    }

    return null;
  }

  /**
   * Proxies incoming Express request to downstream microservice.
   */
  async proxyRequest(req, res, targetServiceUrl) {
    return new Promise((resolve, reject) => {
      const parsedUrl = new URL(targetServiceUrl);
      const targetPath = req.originalUrl;
      
      const isHttps = parsedUrl.protocol === 'https:';
      const transport = isHttps ? https : http;

      // Construct trusted downstream context headers
      const proxyHeaders = {
        ...req.headers,
        host: parsedUrl.host,
        [API_CONSTANTS.HEADER_REQUEST_ID]: req.requestId,
        [API_CONSTANTS.HEADER_CORRELATION_ID]: req.correlationId,
        [API_CONSTANTS.HEADER_TENANT_ID]: req.gatewayContext?.tenantId || 'default-tenant',
        [API_CONSTANTS.HEADER_USER_ID]: req.gatewayContext?.userId || 'anonymous',
        [API_CONSTANTS.HEADER_ROLES]: JSON.stringify(req.gatewayContext?.roles || []),
        [API_CONSTANTS.HEADER_AUTH_METHOD]: req.gatewayContext?.authMethod || 'ANONYMOUS'
      };

      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || (isHttps ? 443 : 80),
        path: targetPath,
        method: req.method,
        headers: proxyHeaders,
        timeout: API_CONSTANTS.DEFAULT_TIMEOUT_MS
      };

      const proxyReq = transport.request(options, (proxyRes) => {
        res.status(proxyRes.statusCode);

        // Copy downstream response headers
        Object.keys(proxyRes.headers).forEach((key) => {
          res.setHeader(key, proxyRes.headers[key]);
        });

        proxyRes.pipe(res);
        proxyRes.on('end', resolve);
      });

      proxyReq.on('timeout', () => {
        proxyReq.destroy();
        reject(new ApiError(HTTP_STATUS.GATEWAY_TIMEOUT, 'Downstream microservice connection timed out', 'GATEWAY_TIMEOUT'));
      });

      proxyReq.on('error', (err) => {
        logger.error('Proxy request failed:', { error: err.message, targetServiceUrl, path: targetPath });
        reject(new ApiError(HTTP_STATUS.BAD_GATEWAY, `Proxy error connecting to downstream service at ${parsedUrl.host}`, 'BAD_GATEWAY'));
      });

      // Stream request body if present
      if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
        const bodyData = typeof req.body === 'object' ? JSON.stringify(req.body) : req.body;
        proxyReq.write(bodyData);
      }

      proxyReq.end();
    });
  }
}

module.exports = new ProxyRoutingService();
