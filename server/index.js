const express = require('express');
const cors = require('cors');
const connectdb = require('./src/config/db');
const apiRoutes = require('./src/routs/apiRoutes');
const historyRoutes = require('./src/routs/historyRouter');

const app = express();
require("dotenv").config();

// Middleswares
app.use(cors());
app.use(express.json());

// Database conection
connectdb();

// Routs
app.use("/api", apiRoutes);
app.use("/history", historyRoutes);


app.get("/", (req, res) => {
  res.send("AI API generator backend is running");
});

// Start the server
const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server is running at the port:${port}`));