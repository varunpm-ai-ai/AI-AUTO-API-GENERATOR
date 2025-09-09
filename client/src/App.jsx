import React from "react";
import { useEffect, useState } from "react";
import Navbar from "./components/navbar/Navbar";
import Sidebar from "./components/sidebars/Sidebar";
import Mainbar from "./components/Mainbar";

const App = () => {
  const [selectedApiId, setSelectedApiId] = useState(null);

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-amber-50">
        <Navbar
        selectedApiId={selectedApiId}
        />
        <Sidebar 
        setSelectedApiId={setSelectedApiId}
        />
      </div>
    </>
  );
};

export default App;
