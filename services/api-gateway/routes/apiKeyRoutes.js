/**
 * API Key Routes for API Gateway
 */
const express = require('express');
const router = express.Router();
const apiKeyController = require('../controllers/apiKeyController');
const { gatewayRateLimiter } = require('../middlewares/rateLimit');

router.post('/', gatewayRateLimiter, apiKeyController.createKey);
router.get('/', apiKeyController.listKeys);
router.delete('/:id', apiKeyController.revokeKey);
router.post('/verify', gatewayRateLimiter, apiKeyController.verifyKeyStatus);

module.exports = router;
