const mongoose = require("mongoose");

const HistorySchema = new mongoose.Schema({
  apiId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Api"
  },
  prompt: {
    type: String,
    required: true
  },
  optionsUsed: {
    type: Object, // API type, operations, endpoints etc.
    default: {}
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model("History", HistorySchema);
