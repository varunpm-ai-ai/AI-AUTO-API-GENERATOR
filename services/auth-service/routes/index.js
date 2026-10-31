/**
 * Central Router Registry for Auth Service
 */
const express = require('express');
const router = express.Router();

const healthRoutes = require('./healthRoutes');
const authRoutes = require('./authRoutes');
const tenantRoutes = require('./tenantRoutes');

// Root health checks
router.use('/', healthRoutes);

// Authentication API routes
router.use('/api/v1/auth', authRoutes);

// Tenant management routes
router.use('/api/v1/auth/tenants', tenantRoutes);

module.exports = router;
