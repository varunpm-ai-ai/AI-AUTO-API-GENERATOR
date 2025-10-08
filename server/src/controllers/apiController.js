// const OpenAI = require("openai");
const { GoogleGenAI  } = require("@google/genai");
const Api = require("../models/ApiSpec");
const History = require('../models/History');
const path = require("path");
const fs = require("fs");

require("dotenv").config();

// Gemini API key
const genAI = new GoogleGenAI (process.env.GEMINI_API_KEY);

// Generate a new api 
exports.generateAPI = async (req, res) => {
  try {
    const { name, type, operations, endpoints, customOptions, code, prompt } = req.body || {};

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    // Build prompt for Gemini
    const fullPrompt = `
      You are an API generator.
      Type: ${type || "REST"}
      Operations: ${operations?.join(", ") || "GET"}
      Endpoints: ${JSON.stringify(endpoints || [{ path: "/", method: "GET" }])}
      Options: ${JSON.stringify(customOptions || {})}
      User Request: ${prompt}
      Generate production-ready API .
    `;

    // Call Gemini
    const response = await genAI.models.generateContent(
      {
        model: "gemini-2.5-flash",
        contents: fullPrompt,
      }
    );
    const generatedCode = response.text;

    const newApi = new Api({
      name: name || prompt.slice(0, 30) || "Generated API",
      type: type || "REST",
      operations: operations || ["GET"],
      endpoints: endpoints || [{ path: "/", method: "GET", description: "Default endpoint" }],
      customOptions: customOptions || {},
      code: generatedCode || code,
    });
    await newApi.save();

    // Save history
    const historyEntry = new History({
      apiId: newApi._id,
      prompt,
      optionsUsed: { type, operations, endpoints, customOptions },
    });
    await historyEntry.save();

    // Send final response
    return res.status(200).json({ api: newApi, history: historyEntry });

  } catch (error) {
    console.error("Error generating API with Gemini:", error);
    if (!res.headersSent) {
      return res.status(500).json({ error: "Error generating API" });
    }
  }
};


// Open ai api key
// const openai = new OpenAI({
//     apiKey: process.env.OPENAI_API_KEY
// });

// Generate a new api 
// exports.generateAPI = async (req, res) => {
//     try {
//         const { name, type, operations, endpoints, customOptions, code, prompt } = req.body || {};

//         // Open ai prompt 
//         const fullPrompt = `
//         You are an API generator.
//         Type: ${type || "REST"}
//         Operations: ${operations?.join(", ") || "GET"}
//         Endpoints: ${JSON.stringify(endpoints || [{ path: "/", method: "GET" }])}
//         Options: ${JSON.stringify(customOptions || {})}
//         User Request: ${prompt}
//         Generate production-ready Node.js Express code for this API.
//         `;

//         // Call OpenAI
//         const response = await openai.chat.completions.create({
//             model: "gpt-4o-mini", // or "gpt-4.1" depending on your plan
//             messages: [{ role: "user", content: fullPrompt }]
//         });

//         const generatedCode = response.choices[0].message.content;

//         // Save the API
//         const newApi = new Api({
//             name: name || prompt?.slice(0, 30) || "Generated API",
//             type: type || "REST",
//             operations: operations || ["GET"],
//             endpoints: endpoints || [{ path: "/", method: "GET", description: "Default endpoint" }],
//             customOptions,
//             code: generatedCode || code
//         })
//         await newApi.save();



//         // Save the history
//         const HistoryEntry = new History({
//             apiId: newApi._id,
//             prompt,
//             optionsUsed: { type, operations, endpoints, customOptions },
//         })
//         await HistoryEntry.save();

//         res.status(200).json({ api: newApi, history: HistoryEntry });
//     } catch (error) {
//         console.log(error);
//         res.status(500).json({ error: "Error generating api" });
//     };
// };

// Get all APIs (Workspace)
exports.getAllApis = async (req, res) => {
  try {
    const apis = await ApiSchema.find().sort({ createdAt: -1 });
    res.json(apis);
  } catch (err) {
    res.status(500).json({ error: "Error fetching workspace APIs" });
  }
};

// Get single API by ID
exports.getApiById = async (req, res) => {
  try {
    const api = await ApiSchema.findById(req.params.id);
    if (!api) return res.status(404).json({ error: "API not found" });
    res.json(api);
  } catch (err) {
    res.status(500).json({ error: "Error fetching API" });
  }
};

// Create new API (manual save)
exports.createApi = async (req, res) => {
  try {
    const { name, type, operations, endpoints, customOptions, code } = req.body;
    const newApi = new Api({ name, type, operations, endpoints, customOptions, code });
    await newApi.save();
    res.status(201).json(newApi);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Update the API
exports.updateApi = async (req, res) => {
  try {
    const { id } = req.params;
    const updatedApi = await Api.findByIdAndUpdate(id, req.body, { new: true });
    if (!updatedApi) return res.status(400).json({ error: "API not found " });
    res.json(updatedApi);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: "Error Updating API " })
  }
};

// Delete the API
exports.deleteApi = async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = await Api.findByIdAndDelete(id);
    if (!deleted) return res.status(404).json({ error: "API not found" });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: "Error deleting API" });
  }
};

// Export API 
exports.exportApi = async (req, res) => {
  try {
    const { id } = req.params;
    const api = await Api.findById(id);

    if (!api) {
      return res.status(404).json({ error: "API not found" });
    }

    // Send the API code as a file
    res.setHeader(
      "Content-Disposition",
      `attachment; filename=${api.name.replace(/\s+/g, "_")}.js`
    );
    res.setHeader("Content-Type", "application/javascript");
    res.send(api.code);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Export failed" });
  }
};


//Search the APIs
exports.searchApis = async (req, res) => {
  try {
    const regex = new RegExp(req.params.query, "i"); 
    const results = await Api.find({ name: { $regex: regex } });
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: "Error searching APIs" });
  }
};