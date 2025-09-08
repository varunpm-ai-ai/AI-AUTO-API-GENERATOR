const mongoose = require("mongoose");

const ApiSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true, 
  },
  type: {
    type: String,
    enum: ["REST", "Auth", "GraphQL", "AI/ML", "3rd Party"], 
    default: "REST" 
  },
  operations: [
    {
      type: String,
      enum: ["GET", "POST", "PUT", "PATCH", "DELETE"] 
    }
  ],
  endpoints: [
    {
      path: { type: String, default: "/" },
      method: { type: String, default: "GET" },
      description: { type: String, default: "Default endpoint" }
    }
  ],
  customOptions: {
    type: Object, 
    default: {}
  },
  code: {
    type: String,
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model("Api", ApiSchema);
