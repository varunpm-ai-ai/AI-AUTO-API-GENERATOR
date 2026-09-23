/**
 * Health Routes for Discovery Service
 */
const express = require('express');
const router = express.Router();
const healthController = require('../controllers/healthController');

router.get('/health', healthController.getHealth);
router.get('/readiness', healthController.getReadiness);

module.exports = router;
