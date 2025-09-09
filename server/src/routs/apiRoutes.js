const express = require('express');
const router = express.Router();
const apiController = require('../controllers/apiController');

//Generate API
router.post("/generate",apiController.generateAPI);

//Workspace API
router.get("/workspace",apiController.getAllApis);
router.post("/workspace", apiController.createApi);

// CRUD with /workspace/:id
router.get("/workspace/:id",apiController.getApiById);
router.put("/workspace/:id",apiController.updateApi);
router.delete("/workspace/:id", apiController.deleteApi);

// Extra routs
router.get("/export/:id", apiController.exportApi);
router.get("/search/:query", apiController.searchApis);

module.exports = router;