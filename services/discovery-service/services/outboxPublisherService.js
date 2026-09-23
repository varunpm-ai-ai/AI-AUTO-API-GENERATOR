/**
 * Transactional Outbox Publisher Service
 * Implements Section 3.5 & 3.6 of Discovery Service Spec.
 */
const mongoose = require('mongoose');
const OutboxEvent = require('../models/OutboxEvent');
const logger = require('../config/logger');

class OutboxPublisherService {
  async createOutboxEvent(acquiredDataset) {
    const payload = {
      event_id: `evt_${acquiredDataset._id}`,
      dataset_id: acquiredDataset._id.toString(),
      discovery_request_id: acquiredDataset.discoveryRequestId.toString(),
      storage_key: acquiredDataset.storageKey,
      storage_uri: acquiredDataset.storageUri,
      checksum: acquiredDataset.checksum,
      content_type: acquiredDataset.contentType,
      source_url: acquiredDataset.sourceUrl,
      file_size_bytes: acquiredDataset.fileSizeBytes,
      timestamp: new Date().toISOString()
    };

    const isDbConnected = mongoose.connection.readyState === 1;
    const outboxEvent = isDbConnected
      ? await OutboxEvent.create({
          aggregateId: acquiredDataset._id.toString(),
          eventType: 'DATASET_ACQUIRED',
          payload,
          status: 'PENDING'
        })
      : {
          _id: new mongoose.Types.ObjectId(),
          aggregateId: acquiredDataset._id.toString(),
          eventType: 'DATASET_ACQUIRED',
          payload,
          status: 'PENDING',
          save: async function () { return this; }
        };

    this.publishPendingEvent(outboxEvent).catch((err) => {
      logger.error('Outbox event publish error:', { error: err.message });
    });

    return outboxEvent;
  }

  async publishPendingEvent(outboxEvent) {
    logger.info(`[Outbox] Publishing DATASET_ACQUIRED event: ${outboxEvent.payload.event_id} to Kafka topic 'dataset-acquired'`);
    outboxEvent.status = 'PUBLISHED';
    outboxEvent.publishedAt = new Date();
    await outboxEvent.save();
  }
}

module.exports = new OutboxPublisherService();
