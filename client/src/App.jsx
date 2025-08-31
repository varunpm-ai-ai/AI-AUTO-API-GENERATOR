import React from "react";
import { useEffect, useState } from "react";
import Navbar from "./components/navbar/Navbar";
import Sidebar from "./components/sidebars/Sidebar";
import Mainbar from "./components/Mainbar";

const App = () => {
  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-amber-50">
        <Navbar/>
        <Sidebar />
      </div>
    </>
  );
};

export default App;
