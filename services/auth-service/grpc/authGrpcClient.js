/**
 * gRPC Client for Auth Service
 * Can be imported by other microservices (API Gateway, Discovery, Dataset Serving)
 */
const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const logger = require('../config/logger');

const PROTO_PATH = path.join(__dirname, '../proto/auth.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const authProto = protoDescriptor.auth;

class AuthGrpcClient {
  constructor(host = process.env.AUTH_GRPC_HOST || 'localhost:50051') {
    this.host = host;
    this.client = null;
    this._initClient();
  }

  _initClient() {
    try {
      this.client = new authProto.AuthService(
        this.host,
        grpc.credentials.createInsecure(),
        {
          'grpc.keepalive_time_ms': 30000,
          'grpc.keepalive_timeout_ms': 5000,
          'grpc.keepalive_permit_without_calls': 1
        }
      );
    } catch (err) {
      logger.warn(`Failed to initialize Auth gRPC client for host ${this.host}: ${err.message}`);
      this.client = null;
    }
  }

  /**
   * Fast synchronous token validation over gRPC
   */
  validateToken(token, timeoutMs = 2000) {
    return new Promise((resolve) => {
      if (!this.client) {
        return resolve({ is_valid: false, error_message: 'Auth gRPC client offline', fallback: true });
      }

      const deadline = new Date(Date.now() + timeoutMs);
      this.client.ValidateToken({ token }, { deadline }, (err, response) => {
        if (err) {
          logger.warn(`Auth gRPC ValidateToken call failed: ${err.message}`);
          return resolve({
            is_valid: false,
            error_message: err.message,
            fallback: true
          });
        }
        resolve(response);
      });
    });
  }

  /**
   * Fast user lookup over gRPC
   */
  getUser(userId, timeoutMs = 2000) {
    return new Promise((resolve) => {
      if (!this.client) {
        return resolve({ found: false, fallback: true });
      }

      const deadline = new Date(Date.now() + timeoutMs);
      this.client.GetUser({ user_id: userId }, { deadline }, (err, response) => {
        if (err) {
          logger.warn(`Auth gRPC GetUser call failed: ${err.message}`);
          return resolve({ found: false, fallback: true });
        }
        resolve(response);
      });
    });
  }

  /**
   * Fast multi-tenant isolation check over gRPC
   */
  verifyTenantAccess(userId, tenantId, requiredRole = '', timeoutMs = 2000) {
    return new Promise((resolve) => {
      if (!this.client) {
        return resolve({ has_access: false, reason: 'Auth gRPC client offline', fallback: true });
      }

      const deadline = new Date(Date.now() + timeoutMs);
      this.client.VerifyTenantAccess(
        { user_id: userId, tenant_id: tenantId, required_role: requiredRole },
        { deadline },
        (err, response) => {
          if (err) {
            logger.warn(`Auth gRPC VerifyTenantAccess call failed: ${err.message}`);
            return resolve({ has_access: false, reason: err.message, fallback: true });
          }
          resolve(response);
        }
      );
    });
  }

  close() {
    if (this.client) {
      this.client.close();
      this.client = null;
    }
  }
}

module.exports = AuthGrpcClient;
