import React, { useState } from "react";
import { Sparkles, Zap } from "lucide-react";

const Mainbar = ({
  previewText,
  setPreviewText,
  onApiGenerated,
  selectedType,
  selectedOps,
  customEndpoints,
  aiDecide,
}) => {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);


  const handleCopy = () => {
    navigator.clipboard
      .writeText(previewText)
      .then(() => {
        alert("Copied to clipboard!");
      })
      .catch((err) => {
        console.error("Failed to copy:", err);
      });
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return alert("Please enter a prompt!");
    const URL = "http://localhost:3000/api/generate";

    setLoading(true);

    try {
      // Map frontend type to backend enum
      const typeMap = {
        "Rest API": "REST",
        "Auth API": "Auth",
        "GraphQL API": "GraphQL",
        "AI/ML API": "AI/ML",
        "3rd Party API": "3rd Party",
      };
      const validOps = ["GET", "POST", "PUT", "PATCH", "DELETE"];
      const filteredOps = selectedOps.filter((op) =>
        validOps.includes(op.toUpperCase())
      );

      // Prepare payload
      const payload = {
        prompt,
        type: typeMap[selectedType] || "REST", // ensure valid enum
        operations: filteredOps,
        endpoints: aiDecide
          ? [{ path: "/", method: "GET", description: "AI decided" }]
          : customEndpoints.map((e) => ({ path: e, method: "GET" })),
        customOptions: {},
      };

      const res = await fetch(URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      console.log("API response:", data); // log for debugging

      // Safely set preview
      if (data.api?.code || data.code) {
        const codeString = data.api?.code ?? data.code;
        setPreviewText(codeString); // update parent state if provided
        setLocalPreview(codeString); // local state ensures immediate rendering
        if (onApiGenerated) onApiGenerated(data.api, data.history);
      } else if (data.error) {
        alert(`Error generating API: ${data.error}`);
      }
    } catch (error) {
      console.error("Error generating API:", error);
      alert("Error generating API. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="">
      <div className="flex flex-col justify-center">
        {/*  Prompt Bar */}
        <div className="relative flex items-center justify-start bg-[#364663] rounded-full px-3 sm:px-4 md:px-20 lg:px-25 py-1 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 ">
          <Sparkles className="w-8 h-8 text-gray-400 " />
          <input
            type="text"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="ml-2 w-full bg-transparent outline-none text-gray-300 "
          />
        </div>

        {/* Prompt Button */}
        <div className="flex ">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="bg-purple-500 hover:bg-purple-400 flex justify-center px-15 py-2 rounded-md mx-auto items-center"
          >
            <Zap />
            <span>{loading ? "Generating..." : "Generate API"}</span>
          </button>
        </div>
      </div>

      {/* preview section */}
      <div
        className="bg-[#364663] mt-5 rounded-xl w-60 sm:w-80 md:w-96 lg:w-[40rem]
        ml-3 h-80 max-h-80 overflow-y-auto relative"
      >
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-300 bg-[#2a364d] px-2 py-1 rounded-md text-sm"
        >
          Copy
        </button>
        <pre className="whitespace-pre-wrap break-words p-4 text-gray-300">
          {previewText}
        </pre>
      </div>
    </div>
  );
};

export default Mainbar;
