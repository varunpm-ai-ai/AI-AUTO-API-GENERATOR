/**
 * gRPC Client for Dataset Catalog Service
 * Synchronous Control & Query Plane (Hybrid Dual-Plane Architecture)
 * Connects to Dataset Catalog Service (default: localhost:50053)
 */
const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const config = require('../config/env');
const logger = require('../config/logger');

const PROTO_PATH = path.join(__dirname, 'dataset_catalog.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const datasetCatalog = protoDescriptor.dataset_catalog;

class CatalogGrpcClient {
  constructor(host = config.CATALOG_GRPC_HOST) {
    this.host = host;
    this.client = null;
    this._initClient();
  }

  _initClient() {
    try {
      this.client = new datasetCatalog.DatasetCatalogService(
        this.host,
        grpc.credentials.createInsecure(),
        {
          'grpc.keepalive_time_ms': 30000,
          'grpc.keepalive_timeout_ms': 5000,
          'grpc.keepalive_permit_without_calls': 1
        }
      );
    } catch (err) {
      logger.warn(`Failed to initialize Catalog gRPC client for host ${this.host}: ${err.message}`);
      this.client = null;
    }
  }

  /**
   * Fast synchronous check for content-addressable duplicate datasets
   * @param {string} checksum SHA-256 hash of dataset content
   * @param {string} storageRef Optional storage URI reference
   * @param {number} timeoutMs Deadline timeout in ms
   * @returns {Promise<Object>} CheckDuplicateResponse or safe fallback
   */
  async checkDuplicate(checksum, storageRef = '', timeoutMs = 2000) {
    if (!this.client) {
      return { is_duplicate: false, fallback: true };
    }
    return new Promise((resolve) => {
      const deadline = new Date(Date.now() + timeoutMs);
      this.client.CheckDuplicate({ checksum, storage_ref: storageRef }, { deadline }, (err, response) => {
        if (err) {
          logger.warn(`gRPC CheckDuplicate call fallback: ${err.message}`);
          return resolve({ is_duplicate: false, fallback: true });
        }
        resolve(response);
      });
    });
  }

  /**
   * Identity resolution by name, source, and domain
   */
  async resolveIdentity(name, source = '', domain = '', timeoutMs = 2000) {
    if (!this.client) {
      return { is_existing: false, dataset_id: null, fallback: true };
    }
    return new Promise((resolve) => {
      const deadline = new Date(Date.now() + timeoutMs);
      this.client.ResolveIdentity({ name, source, domain }, { deadline }, (err, response) => {
        if (err) {
          logger.warn(`gRPC ResolveIdentity call fallback: ${err.message}`);
          return resolve({ is_existing: false, dataset_id: null, fallback: true });
        }
        resolve(response);
      });
    });
  }

  /**
   * Register a new dataset or new version directly in catalog via gRPC
   */
  async registerDataset(payload, timeoutMs = 3000) {
    if (!this.client) {
      return null;
    }
    return new Promise((resolve) => {
      const deadline = new Date(Date.now() + timeoutMs);
      this.client.RegisterDataset(payload, { deadline }, (err, response) => {
        if (err) {
          logger.warn(`gRPC RegisterDataset call fallback: ${err.message}`);
          return resolve(null);
        }
        resolve(response);
      });
    });
  }

  close() {
    if (this.client) {
      this.client.close();
    }
  }
}

const defaultClient = new CatalogGrpcClient();
module.exports = defaultClient;
module.exports.CatalogGrpcClient = CatalogGrpcClient;
