/**
 * gRPC Server Implementation for Auth Service
 * Provides Synchronous Inter-Service Identity & Tenant Boundary Verification
 */
const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const config = require('../config/env');
const logger = require('../config/logger');
const AuthService = require('../services/authService');
const TenantService = require('../services/tenantService');
const Storage = require('../models/storage');

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

class AuthGrpcServer {
  constructor(port = config.GRPC_PORT) {
    this.port = port;
    this.server = new grpc.Server({
      'grpc.max_receive_message_length': 4 * 1024 * 1024,
      'grpc.max_send_message_length': 4 * 1024 * 1024
    });
    this._bindServices();
  }

  _bindServices() {
    this.server.addService(authProto.AuthService.service, {
      ValidateToken: this.validateToken.bind(this),
      GetUser: this.getUser.bind(this),
      VerifyTenantAccess: this.verifyTenantAccess.bind(this),
      GetTenant: this.getTenant.bind(this)
    });
  }

  async validateToken(call, callback) {
    try {
      const { token } = call.request;
      const result = await AuthService.validateToken(token);

      callback(null, {
        is_valid: result.isValid,
        user_id: result.userId || '',
        tenant_id: result.tenantId || '',
        email: result.email || '',
        roles: result.roles || [],
        error_message: result.errorMessage || ''
      });
    } catch (err) {
      logger.error('gRPC ValidateToken error:', { error: err.message });
      callback(null, {
        is_valid: false,
        user_id: '',
        tenant_id: '',
        email: '',
        roles: [],
        error_message: err.message
      });
    }
  }

  async getUser(call, callback) {
    try {
      const { user_id } = call.request;
      const user = await Storage.findUserById(user_id);

      if (!user) {
        return callback(null, {
          found: false,
          user_id: '',
          tenant_id: '',
          email: '',
          name: '',
          role: '',
          status: ''
        });
      }

      callback(null, {
        found: true,
        user_id: user.userId,
        tenant_id: user.tenantId,
        email: user.email,
        name: user.name,
        role: user.role,
        status: user.status
      });
    } catch (err) {
      logger.error('gRPC GetUser error:', { error: err.message });
      callback(null, { found: false });
    }
  }

  async verifyTenantAccess(call, callback) {
    try {
      const { user_id, tenant_id, required_role } = call.request;
      const result = await TenantService.verifyTenantAccess(user_id, tenant_id, required_role || null);

      callback(null, {
        has_access: result.hasAccess,
        reason: result.reason
      });
    } catch (err) {
      logger.error('gRPC VerifyTenantAccess error:', { error: err.message });
      callback(null, {
        has_access: false,
        reason: err.message
      });
    }
  }

  async getTenant(call, callback) {
    try {
      const { tenant_id } = call.request;
      const tenant = await Storage.findTenantById(tenant_id);

      if (!tenant) {
        return callback(null, {
          found: false,
          tenant_id: '',
          name: '',
          slug: '',
          plan: '',
          status: ''
        });
      }

      callback(null, {
        found: true,
        tenant_id: tenant.tenantId,
        name: tenant.name,
        slug: tenant.slug,
        plan: tenant.plan,
        status: tenant.status
      });
    } catch (err) {
      logger.error('gRPC GetTenant error:', { error: err.message });
      callback(null, { found: false });
    }
  }

  start() {
    return new Promise((resolve, reject) => {
      const bindAddress = `0.0.0.0:${this.port}`;
      this.server.bindAsync(bindAddress, grpc.ServerCredentials.createInsecure(), (err, boundPort) => {
        if (err) {
          logger.error(`Failed to bind Auth gRPC server to ${bindAddress}:`, { error: err.message });
          return reject(err);
        }
        logger.info(`⚡ Auth Service gRPC Server running on port ${boundPort}`);
        resolve(boundPort);
      });
    });
  }

  stop() {
    return new Promise((resolve) => {
      this.server.tryShutdown(() => {
        logger.info('Auth gRPC server stopped successfully.');
        resolve();
      });
    });
  }
}

module.exports = AuthGrpcServer;
