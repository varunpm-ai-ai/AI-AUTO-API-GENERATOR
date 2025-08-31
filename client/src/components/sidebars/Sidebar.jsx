import React, { useState } from "react";
import { useEffect } from "react";
import {
  HistoryIcon,
  ListStart,
  Lock,
  Logs,
  Route,
  Search,
} from "lucide-react";
import Mainbar from "../Mainbar";
import Navbar from "../navbar/Navbar";

const APITypes = [
  { firstName: "Rest API", id: 1 },
  { firstName: "Auth API", id: 2 },
  { firstName: "GraphQL API", id: 3 },
  { firstName: "AI/ML API", id: 4 },
  { firstName: "3rd Party", id: 5 },
];

const OperationTypes = [
  { firstName2: "GET", id: 6 },
  { firstName2: "PUT", id: 7 },
  { firstName2: "POST", id: 8 },
  { firstName2: "PATCH", id: 9 },
  { firstName2: "DELETE", id: 10 },
];

const Sidebar = () => {
  const [active, setActive] = useState(false);
  const [apiTypes, setAPiTypes] = useState(false);
  const [oprations, setOprations] = useState(false);
  const [endPoints, setEndPoints] = useState(false);
  const [history, setHistory] = useState(false);
  const [searchItem, setSearchItem] = useState("");
  const [filteredUsers, setFilteredUsers] = useState(APITypes);
  const [filteredUsers2, setFilteredUsers2] = useState(OperationTypes);
  const [items, setItems] = useState([]);
  const [workspaceItems, setWorkspaceItems] = useState([]);
  const [historyItems, setHistoryitems] = useState([]);
  const [previewText, setPreviewText] = useState("API");
  const [selectedType, setSelectedType] = useState("REST");
  const [selectedOps, setSelectedOps] = useState([]);
  const [customEndpoints, setCustomEndpoints] = useState([]);
  const [aiDecide, setAiDecide] = useState(false);
  // const [selectedApiId, setSelectedApiId] = useState(null);

  const isAnyActive = active || apiTypes || oprations || endPoints || history;

  useEffect(() => {
    fetch("http://localhost:3000/api/workspace")
      .then((res) => res.json())
      .then((data) => setWorkspaceItems(data))
      .catch((error) => console.log(error));

    fetch("http://localhost:3000/history")
      .then((res) => res.json())
      .then((data) => setHistoryitems(data))
      .catch((error) => console.log(error));
  }, []);

  useEffect(() => {
    setTimeout(() => {
      setItems([]);
    });
  }, []);

  const handleInputChange = (e) => {
    const searchTerm = e.target.value;
    setSearchItem(searchTerm);

    const filteredItems = APITypes.filter((APIs) =>
      APIs.firstName.toLowerCase().includes(searchTerm.toLowerCase())
    );

    setFilteredUsers(filteredItems);
  };

  const handleInputChange2 = (e) => {
    const searchTerm = e.target.value;
    setSearchItem(searchTerm);

    const filteredItems2 = OperationTypes.filter((Ops) =>
      Ops.firstName2.toLowerCase().includes(searchTerm.toLowerCase())
    );

    setFilteredUsers2(filteredItems2);
  };

  const defaultWorkspace = () => {
    setActive(!active);
    setAPiTypes(false);
    setOprations(false);
    setEndPoints(false);
    setHistory(false);
  };

  const handleAPITypes = () => {
    setActive(false);
    setAPiTypes(!apiTypes);
    setOprations(false);
    setEndPoints(false);
    setHistory(false);
  };

  const Oprations = () => {
    setActive(false);
    setAPiTypes(false);
    setOprations(!oprations);
    setEndPoints(false);
    setHistory(false);
  };

  const Endpoints = () => {
    setActive(false);
    setAPiTypes(false);
    setOprations(false);
    setEndPoints(!endPoints);
    setHistory(false);
  };

  const History = () => {
    setActive(false);
    setAPiTypes(false);
    setOprations(false);
    setEndPoints(false);
    setHistory(!history);
  };

  const handleUpdate = async (id) => {
    const newName = prompt("Enter new API name");
    if (!newName) return;

    try {
      url = `http://localhost:3000/api/workspace/${id}`;

      const res = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      });
      const data = await res.json();

      // Update frontend list
      setWorkspaceItems((prev) =>
        prev.map((item) => (item._id === id ? updated : item))
      );
    } catch (error) {
      console.error("Error updating:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this API?")) return;

    try {
      url = `http://localhost:3000/api/workspace/${id}`

      await fetch(url, {
        method: "DELETE",
      });

      // Remove from frontend
      setWorkspaceItems((prev) => prev.filter((item) => item._id !== id));
    } catch (err) {
      console.error("Error deleting:", err);
    }
  };

  const handleSearch = async (query) => {
  const res = await fetch(`http://localhost:3000/api/search/${query}`);
  const data = await res.json();
  setWorkspaceItems(data);
};


  return (
    <>
      <div className="flex h-screen">
        {/* Small Sidebar */}
        <div className="w-20% bg-gray-700 flex flex-col items-center py-2.5 space-y-9">
          {/* Icons only */}

          {/*  Lock Security */}
          <div
            onClick={defaultWorkspace}
            className="w-18 h-11 flex items-center cursor-pointer 
            justify-center border-b-2 border-gray-500 hover:bg-gray-600 "
          >
            <Lock />
          </div>

          {/* Types of APIs */}
          <div
            onClick={handleAPITypes}
            className="hover:bg-gray-600 px-3 py-2 text-sm flex justify-center flex-col cursor-pointer rounded-md"
          >
            <ListStart className="ml-1" />
            <span>Types</span>
          </div>

          {/* Types of oprations */}
          <div
            onClick={Oprations}
            className="hover:bg-gray-600 px-4 py-2 cursor-pointer rounded-md"
          >
            <Logs className="ml-.5" />
            <span>Ops</span>
          </div>

          {/* Endpoint costomisation */}
          <div
            onClick={Endpoints}
            className="hover:bg-gray-600 px-3 py-2 cursor-pointer rounded-md"
          >
            <Route className="ml-1" />
            <span>Ends</span>
          </div>

          {/* History */}
          <div
            onClick={History}
            className="hover:bg-gray-600 px-1 py-2 cursor-pointer rounded-md "
          >
            <HistoryIcon className="ml-3.5" width={20} height={20} />
            <span>History</span>
          </div>
        </div>

        {active && (
          <>
            {/* large Sidebar */}
            <div className="w-2/4 sm:w-2/4 md:w-1/4 lg:w-1/4 bg-[#1e293b] text-gray-200 flex flex-col ">
              {/* Title / Logo */}
              <div className="text-sm sm:text-md md:text-xl lg:text-xl font-bold mb-6 border-b-2 border-gray-500 pb-2 mt-6 sm:mt-1 md:mt-4 lg:mt-[15.7px]">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;My Workspace
              </div>

              {/* Workspace Search Bar */}
              <div className="relative flex items-center bg-[#364663] rounded-full px-3 py-3 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 ">
                <Search className="w-8 h-8 text-gray-400 z-10" />
                <input
                  onClick={handleSearch}
                  type="text"
                  placeholder="Search your APIs here"
                  className="ml-2 w-full bg-transparent outline-none text-gray-300"
                />
              </div>
              <label className="flex justify-center text-[9px] sm:text-[9px] md:text-sm lg:text-md">
                {" "}
                You can see your generated APIs here
              </label>
              <ul className="cursor-pointer space-y-2 m-5 overflow-auto">
                {workspaceItems.length > 0 &&
                  workspaceItems.map((item, i) => {
                    <li
                      key={item._id}
                      onClick={() => setPreviewText(item.code)}
                      className="p-2 rounded-md bg-gray-600 hover:bg-gray-700 flex justify-between"
                    >
                      <span>{item.name || "Unnamed API"}</span>
                      <div className="flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpdate(item._id);
                          }}
                          className="bg-blue-400 rounded-md px-1 hover:bg-blue-300"
                        >
                          Update
                        </button>
                        <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(item._id);
                        }}
                        className="bg-blue-400 rounded-md px-1 hover:bg-blue-300">
                          Delete
                        </button>
                      </div>
                    </li>;
                  })}
              </ul>
            </div>
          </>
        )}

        {apiTypes && (
          <>
            {/* large Sidebar */}
            <div className="w-2/4 sm:w-2/4 md:w-1/4 lg:w-1/4 bg-[#1e293b] text-gray-200 flex flex-col ">
              {/* Title / Logo */}
              <div className="text-sm sm:text-md md:text-xl lg:text-xl font-bold mb-6 border-b-2 border-gray-500 pb-2 mt-6 sm:mt-1 md:mt-4 lg:mt-[15.7px]">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;My Workspace
              </div>

              {/* Workspace Search Bar */}
              <div>
                <div className="relative flex items-center bg-[#364663] rounded-full px-3 py-1 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 ">
                  <Search className="w-8 h-8 text-gray-400 z-10" />
                  <input
                    type="text"
                    value={searchItem}
                    onChange={handleInputChange}
                    placeholder="Search your API types here"
                    className="ml-2 w-full bg-transparent outline-none text-gray-300"
                  />
                </div>
                <label className="flex justify-center">
                  {" "}
                  Select your API types
                </label>
                <ul className="felx m-5 space-y-2">
                  {filteredUsers.map((APIs) => (
                    <li key={APIs.id}>
                      <input
                        type="radio"
                        name="same"
                        checked={selectedType === APIs.firstName}
                        onChange={() => setSelectedType(APIs.firstName)}
                      />
                      <span>{APIs.firstName}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )}

        {oprations && (
          <>
            {/* large Sidebar */}
            <div className="w-2/4 sm:w-2/4 md:w-1/4 lg:w-1/4 bg-[#1e293b] text-gray-200 flex flex-col ">
              {/* Title / Logo */}
              <div className="text-sm sm:text-md md:text-xl lg:text-xl font-bold mb-6 border-b-2 border-gray-500 pb-2 mt-6 sm:mt-1 md:mt-4 lg:mt-[15.7px]">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;My Workspace
              </div>

              {/* Workspace Search Bar */}
              <div className="relative flex items-center bg-[#364663] rounded-full px-3 py-1 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 ">
                <Search className="w-8 h-8 text-gray-400 z-10" />
                <input
                  type="text"
                  value={searchItem}
                  onChange={handleInputChange2}
                  placeholder="Search your operation here"
                  className="ml-2 w-full bg-transparent outline-none text-gray-300"
                />
              </div>
              <label className="flex justify-center">
                {" "}
                Select your oprations
              </label>
              <ul className="felx m-5 space-y-2">
                {filteredUsers2.map((Ops) => (
                  <li key={Ops.id}>
                    <input
                      type="checkbox"
                      checked={selectedOps.includes(Ops.firstName2)}
                      onChange={() => {
                        if (selectedOps.includes(Ops.firstName2)) {
                          setSelectedOps(
                            selectedOps.filter((o) => o !== Ops.firstName2)
                          );
                        } else {
                          setSelectedOps([...selectedOps, Ops.firstName2]);
                        }
                      }}
                    />
                    <span>{Ops.firstName2}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}

        {endPoints && (
          <>
            {/* large Sidebar */}
            <div className="w-2/4 sm:w-2/4 md:w-1/4 lg:w-1/4 bg-[#1e293b] text-gray-200 flex flex-col ">
              {/* Title / Logo */}
              <div className="text-sm sm:text-md md:text-xl lg:text-xl font-bold mb-6 border-b-2 border-gray-500 pb-2 mt-6 sm:mt-1 md:mt-4 lg:mt-[15.7px]">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;My Workspace
              </div>

              {/* Let AI Deside */}
              <label
                className="flex justify-center
              text-md
              "
              >
                Let AI deside
              </label>

              <div className="space-x-2 text-gray-300 hover:text-gray-400 cursor-pointer mt-2 ml-4">
                <input
                  type="checkbox"
                  checked={aiDecide}
                  onChange={() => setAiDecide(!aiDecide)}
                  name="GET"
                  id="GET"
                />
                <span>AI END_POINTS</span>
              </div>

              {/* Custom Endpoints */}
              <label
                className="flex justify-center
              text-[12px] sm:text-[12px] md:text-sm lg:text-lg mt-15
              "
              >
                Enter Your Custom Endpoints
              </label>

              <div className="relative flex items-center bg-[#364663] rounded-sm px-3 py-1 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 mt-4">
                {/* <Search className="w-8 h-8 text-gray-400 z-10" /> */}
                <textarea
                  placeholder="Enter your custom endpoints here"
                  className="ml-2 w-full bg-transparent outline-none text-gray-300 "
                  value={customEndpoints.join("\n")}
                  onChange={(e) =>
                    setCustomEndpoints(e.target.value.split("\n"))
                  }
                />
              </div>
            </div>
          </>
        )}

        {history && (
          <>
            {/* large Sidebar */}
            <div className="w-2/4 sm:w-2/4 md:w-1/4 lg:w-1/4 bg-[#1e293b] text-gray-200 flex flex-col ">
              {/* Title / Logo */}
              <div className="text-sm sm:text-md md:text-xl lg:text-xl font-bold mb-6 border-b-2 border-gray-500 pb-2 mt-6 sm:mt-1 md:mt-4 lg:mt-[15.7px]">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;My Workspace
              </div>

              {/* Workspace Search Bar */}
              <div className="relative flex items-center bg-[#364663] rounded-full px-3 py-1 mb-5 overflow-hidden mx-2 sm:mx-2 md:mx-3 lg:mx-3 ">
                <Search className="w-8 h-8 text-gray-400 z-10" />
                <input
                  type="text"
                  placeholder="Search your history here"
                  className="ml-2 w-full bg-transparent outline-none text-gray-300"
                />
              </div>
              <label className="flex justify-start ml-3"> Your history</label>
              <ul className="cursor-pointer space-y-2 m-5 overflow-auto">
                {historyItems.length > 0 &&
                  historyItems.map((entry, i) => {
                    <li
                      key={i}
                      onClick={() =>
                        setPreviewText(entry.apiId?.code || entry.prompt)
                      }
                      className="p-2 rounded-md pr-20 bg-gray-600 hover:bg-gray-700"
                    >
                      <span>{entry.optionsUsed?.type || "API"}</span> -{" "}
                      <span className="text-xs">
                        {new Date(entry.timestamp).toLocaleString()}
                      </span>
                    </li>;
                  })}
              </ul>
            </div>
          </>
        )}

        {/* Midpart */}
        <div
          className={`${
            isAnyActive ? "hidden md:flex" : ""
          } justify-center mx-auto mt-8`}
        >
          <Mainbar
            previewText={previewText}
            setPreviewText={setPreviewText}
            onApiGenerated={(newApi, HistoryEntry) => {
              setWorkspaceItems((prev) => [...prev, newApi]);
              setHistoryitems((prev) => [...prev, HistoryEntry]);
            }}
            selectedType={selectedType}
            selectedOps={selectedOps}
            customEndpoints={customEndpoints}
            aiDecide={aiDecide}
          />
        </div>
      </div>
    </>
  );
};

export default Sidebar;
