/**
 * Health & Readiness Routes
 */
const express = require('express');
const router = express.Router();
const HealthController = require('../controllers/healthController');

router.get('/health', HealthController.getHealth);
router.get('/readiness', HealthController.getReadiness);

module.exports = router;
