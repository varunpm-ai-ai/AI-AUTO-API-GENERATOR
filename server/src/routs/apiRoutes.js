const express = require('express');
const router = express.Router();
const apiController = require('../controllers/apiController');

router.post("/generate",apiController.generateAPI);
router.get("/workspace",apiController.getAllApis);
router.post("/workspace", apiController.createApi);
router.get("/:id",apiController.getApiById);
router.put("/:id",apiController.updateApi);
router.delete("/:id", apiController.deleteApi);
router.get("/export/:id", apiController.exportApi);
router.get("/search/:query", apiController.searchApis);

module.exports = router;