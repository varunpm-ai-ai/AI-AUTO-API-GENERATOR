/**
 * Gateway Reverse Proxy Routes
 */
const express = require('express');
const router = express.Router();
const gatewayController = require('../controllers/gatewayController');
const { gatewayRateLimiter } = require('../middlewares/rateLimit');

router.get('/info', gatewayController.getGatewayInfo);
router.all('/*', gatewayRateLimiter, gatewayController.proxyRouteHandler);

module.exports = router;
