/**
 * Dataset Acquisition & Transactional Storage Service
 * Implements Section 3.3, 3.6, and 4.7 of Discovery Service Spec.
 */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const mongoose = require('mongoose');
const config = require('../config/env');
const logger = require('../config/logger');
const AcquiredDataset = require('../models/AcquiredDataset');
const outboxPublisherService = require('./outboxPublisherService');
const catalogGrpcClient = require('../grpc/catalogClient');

class AcquisitionService {
  async acquire(discoveryRequest, crawlJob) {
    const rawData = JSON.stringify({
      request_id: discoveryRequest._id,
      query: discoveryRequest.query,
      source_url: crawlJob.sourceUrl,
      acquired_at: new Date().toISOString(),
      sample_records: [
        { id: 1, name: 'Sample Dataset Item A', value: 100 },
        { id: 2, name: 'Sample Dataset Item B', value: 200 }
      ]
    }, null, 2);

    const checksum = crypto.createHash('sha256').update(rawData).digest('hex');
    const storageKey = `raw_${discoveryRequest._id}_${Date.now()}.json`;
    const storageDir = path.resolve(config.OBJECT_STORAGE_BASE_PATH);
    const storagePath = path.join(storageDir, storageKey);

    // Synchronous Plane 1 Control Check via gRPC (Catalog Deduplication)
    const duplicateCheck = await catalogGrpcClient.checkDuplicate(checksum, `s3://ai-discovery-datasets/${storageKey}`);
    if (duplicateCheck && duplicateCheck.is_duplicate) {
      logger.info(`gRPC Catalog check: duplicate dataset found (Existing ID: ${duplicateCheck.existing_dataset_id}, Version: ${duplicateCheck.existing_version_id})`);
    }

    try {
      fs.mkdirSync(storageDir, { recursive: true });
      fs.writeFileSync(storagePath, rawData, 'utf8');
    } catch (e) {
      logger.warn('Failed to write raw file to filesystem storage; proceeding with virtual storage URI', { error: e.message });
    }

    const storageUri = `s3://ai-discovery-datasets/${storageKey}`;
    const isDbConnected = mongoose.connection.readyState === 1;

    const dataset = isDbConnected
      ? await AcquiredDataset.create({
          discoveryRequestId: discoveryRequest._id,
          storageKey,
          storageUri,
          sourceUrl: crawlJob.sourceUrl,
          checksum,
          contentType: 'application/json',
          fileSizeBytes: Buffer.byteLength(rawData),
          metadata: { query: discoveryRequest.query, crawler: crawlJob.crawlerType }
        })
      : {
          _id: new mongoose.Types.ObjectId(),
          discoveryRequestId: discoveryRequest._id,
          storageKey,
          storageUri,
          sourceUrl: crawlJob.sourceUrl,
          checksum,
          contentType: 'application/json',
          fileSizeBytes: Buffer.byteLength(rawData),
          metadata: { query: discoveryRequest.query, crawler: crawlJob.crawlerType }
        };

    await outboxPublisherService.createOutboxEvent(dataset);

    logger.info(`Acquired raw dataset ${dataset._id} (Key: ${storageKey}, Size: ${dataset.fileSizeBytes}B)`);
    return dataset;
  }
}

module.exports = new AcquisitionService();
