import React, { useState, useEffect } from "react";
import MobileNav from "./MobileNav";
import { Bars3Icon } from "@heroicons/react/24/outline";
import { Bell, FileUp, Search, Settings, User } from "lucide-react";

const Navbar = () => {
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const [isActive, setIsActive] = useState(false);
  const [items, setItems] = useState([]);

  useEffect(() => {
    setTimeout(() => {
      setItems([]);
    }, 2000);
  }, []);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const toggleSidebar = () => {
    if (windowWidth < 768) {
      setIsSmallScreen(!isSmallScreen);
    }
  };

  const OpenSearchTab = () => {
    setIsActive(!isActive);
  };

  return (
    <>
      <div className="w-full bg-gradient-to-r from-[#0b1120] to-[#1a2130] shadow-md border-b border-gray-700 py-3 flex items-center justify-between">
        {/* Left Nav links */}
        <div className="flex space-x-5 items-center">
          <div className="ml-4" onClick={toggleSidebar}>
            <Bars3Icon className="w-7 h-7 cursor-pointer" />
          </div>
          <a href="#" className="text-gray-300 hover:text-gray-400">
            Home
          </a>
          <a href="#" className="text-gray-300 hover:text-gray-400">
            WorkSpace
          </a>
          <a href="#" className="text-gray-300 hover:text-gray-400">
            Test Your APIs
          </a>
        </div>

        {/* Search Bar For Large Screens */}
        <div
          onClick={OpenSearchTab}
          className="hidden md:flex items-center bg-[#222c3d] rounded-full px-3 py-1 w-25%"
        >
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search your APIs..."
            className="ml-2 w-full bg-transparent outline-none text-gray-300 placeholder-gray-500"
          />
        </div>

        {/* Right part */}
        <div className="hidden md:flex ">
          <div className="flex space-x-6 sm:space-x-1 md:space-x-3 lg:space-x-5 mr-4">
            <div className="mt-1 bg-gray-600 hover:bg-gray-500 py-2 px-5 rounded-md">
              <Settings />
            </div>
            <div className="mt-1 bg-gray-600 hover:bg-gray-500 py-2 px-5 rounded-md">
              <Bell />
            </div>
            <div className="mt-1 bg-gray-600 hover:bg-gray-500 py-2 px-5 rounded-md">
              <User />
            </div>

            <div className="bg-gray-600 hover:bg-gray-500 rounded-md p-0.5 flex ">
              <button type="button" className="flex gap-1 px-2 py-2">
                <FileUp />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar only for small screens */}
        {isSmallScreen && windowWidth < 768 && (
          <MobileNav closeSidebar={() => setIsSmallScreen(false)} />
        )}
      </div>

      {isActive && (
        <div className="hidden md:flex fixed bg-gray-800 w-full mx-18 z-11 h-48 max-h-50 overflow-y-auto overflow-x-auto rounded-xl">
          <span className="m-5">
            <ul className="cursor-pointer space-y-2">
              {items.lengh > 0 &&
                items.map(() => (
                  <li className=" p-2 rounded-md pr-250 hover:bg-gray-600">
                    {items}
                  </li>
                ))}
            </ul>
          </span>
        </div>
      )}
    </>
  );
};

export default Navbar;
