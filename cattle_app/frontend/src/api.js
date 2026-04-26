import axios from "axios";

const API = axios.create({ baseURL: "http://127.0.0.1:8000" });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const registerUser = (payload) => API.post("/register", payload);
export const loginUser = (payload) => API.post("/login", payload);
export const listCattle = () => API.get("/cattle");
export const addCattle = (formData) => API.post("/cattle", formData);
export const buyCattle = (id) => API.post(`/buy/${id}`);
export const getNotifications = () => API.get("/notifications");
