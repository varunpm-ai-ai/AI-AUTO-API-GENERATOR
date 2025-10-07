# AI-AUTO-API-GENERATOR
Using AI to Create APIs to save production time 

# 🚀 AI Auto API Generator

A full-stack **AI-powered API generator** that lets you create, manage, and export backend APIs using OpenAI + Node.js + MongoDB.  
The app provides a UI to generate APIs from prompts, manage them in a workspace, track history, and export code.

---

## ✨ Features
- 🔹 **AI-Generated APIs** – Generate REST/GraphQL/Auth APIs with custom options
- 🔹 **Workspace** – Save all generated APIs in MongoDB, view and manage them
- 🔹 **History** – Track when and what was generated, linked to prompts
- 🔹 **Update & Delete** – Modify or remove APIs directly from the UI
- 🔹 **Search** – Filter APIs in workspace using MongoDB queries
- 🔹 **Export** – Download generated API code as a file
- 🔹 **Frontend** – React + Tailwind (clean UI with sidebar, main preview, and controls)
- 🔹 **Backend** – Node.js + Express + MongoDB + OpenAI API

---

## 🛠️ Tech Stack
**Frontend:** React, Tailwind, Lucide-React  
**Backend:** Node.js, Express.js  
**Database:** MongoDB (Mongoose ODM)  
**AI Integration:** OpenAI API  

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-auto-api-generator.git
cd ai-auto-api-generator


### 2. Backend Setup
cd server
npm install

MONGO_URI=your_mongo_connection_string
GEMINI_API_KEY=your_openai_key
PORT=3000

npm run dev

### 3. Frontend Setup
cd client
npm install
npm start


Screen shots
![image alt](https://github.com/varunpm-ai-ai/AI-AUTO-API-GENERATOR/blob/b652445d9dab9374091f4cc23f3f6c2f2e4ff372/screenshots/image1.png)


 API Routes
Workspace
POST /api/generate → Generate new API
GET /api/workspace → Get all APIs
GET /api/workspace/:id → Get API by ID
PUT /api/workspace/:id → Update API
DELETE /api/workspace/:id → Delete API
GET /api/export/:id → Export API code as file
History
GET /history → Get all history entries



##  Future Improvements
- Authentication (multi-user workspaces)
- Better export formats (`.zip` with full project boilerplate)
- Richer prompt options (rate limits, DB integration, middlewares)
- Pagination for history/workspace
- **Hopscotch integration** in the *Test Your API* section (guided API testing)
- **Dedicated Workspace Page** – on clicking workspace, show a full page with all workspace management features





🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.


MIT License

---

This will make your repo look **professional and complete**.  
You can also add badges (e.g. for Node.js, React, MongoDB, license) at the top for polish.  

👉 Do you want me to also generate a **README with badges + emojis style** (like a “GitHub trending” project look)?

