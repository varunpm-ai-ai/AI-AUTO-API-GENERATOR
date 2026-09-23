/**
 * Discovery API Routes
 */
const express = require('express');
const router = express.Router();
const discoveryController = require('../controllers/discoveryController');
const discoveryRateLimiter = require('../middlewares/rateLimit');

router.post('/', discoveryRateLimiter, discoveryController.initiateDiscovery);
router.get('/:id', discoveryController.getDiscovery);
router.get('/:id/sources', discoveryController.getDiscoverySources);
router.get('/:id/jobs', discoveryController.getDiscoveryJobs);

module.exports = router;
