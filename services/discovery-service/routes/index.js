/**
 * Central Router Registry for Discovery Service Microservice
 */
const express = require('express');
const router = express.Router();

const healthRoutes = require('./healthRoutes');
const discoveryRoutes = require('./discoveryRoutes');

// Public Health routes
router.use('/', healthRoutes);

// Discovery API routes
router.use('/api/v1/discover', discoveryRoutes);

module.exports = router;
