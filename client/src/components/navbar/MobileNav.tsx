import React from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { Bell, FileUp, Search, Settings, User } from "lucide-react";

const MobileNav = ({ closeSidebar }) => {
  return (
    <>
      <div className="fixed top-0 left-0 w-50 h-full bg-gray-900 text-white z-50 p-5 flex flex-col ">
        {/* Close button */}
        <div className="self-start mb-5 cursor-pointer" onClick={closeSidebar}>
          <XMarkIcon className="w-6 h-6" />
        </div>

        {/* Mobile Search Bar */}
        <div className="relative flex items-center bg-[#222c3d] rounded-full px-3 py-1 mb-5 overflow-hidden">
          <Search className="w-8 h-8 text-gray-400 z-10" />
          <input
            type="text"
            className="ml-2 w-full bg-transparent outline-none text-gray-300"
          />
        </div>

        {/* Utilities */}
        <div className="space-y-5 ml-1.5">
          <div className="bg-purple-600 hover:bg-purple-500 rounded-xl flex p-2 space-x-5">
            <Settings /> <span>Settings</span>
          </div>
          <div className="bg-purple-600 hover:bg-purple-500 rounded-xl flex p-2 space-x-3">
            <Bell /> <span>Notifiactions</span>
          </div>
          <div className="bg-purple-600 hover:bg-purple-500 rounded-xl flex p-2 space-x-6">
            {" "}
            <User /> <span>Account</span>
          </div>
          <div className="bg-purple-600 hover:bg-purple-500 rounded-xl p-2 flex ">
            <button type="button" className="flex gap-7">
              <FileUp />
              Export
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default MobileNav;
