const History  = require('../models/History');

// Get all history
exports.getAllHistory = async (req, res) => {
  try {
    const history = await History.find()
      .populate("apiId")
      .sort({ timestamp: -1 });
    res.json(history);
  } catch (err) {
    res.status(500).json({ error: "Error fetching history" });
  }
};
