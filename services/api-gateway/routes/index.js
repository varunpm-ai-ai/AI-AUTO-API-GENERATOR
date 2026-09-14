/**
 * Central Router Registry for API Gateway Microservice
 */
const express = require('express');
const router = express.Router();

const healthRoutes = require('./healthRoutes');
const apiKeyRoutes = require('./apiKeyRoutes');
const gatewayRoutes = require('./gatewayRoutes');

// Public Health routes
router.use('/', healthRoutes);

// API Key management routes
router.use('/api/v1/keys', apiKeyRoutes);

// Gateway Proxy routes
router.use('/api/v1/gateway', gatewayRoutes);

module.exports = router;
