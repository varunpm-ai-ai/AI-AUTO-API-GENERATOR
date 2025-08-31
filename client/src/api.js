import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:3000", // backend base URL
});

export default API;
