import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — attempt token refresh, then redirect to login
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // TODO(TASK-1.05): Implement token refresh logic
      useAuthStore.getState().clearAuth();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// API methods for Phase 2: Core Risk Management Engine

export async function getRiskMatrix() {
  const response = await api.get("/config/risk-matrix");
  return response.data;
}

export async function getRisks() {
  const response = await api.get("/risks");
  return response.data;
}

export async function getRisk(id: string) {
  const response = await api.get(`/risks/${id}`);
  return response.data;
}

export async function createRisk(data: any) {
  const response = await api.post("/risks", data);
  return response.data;
}

export async function updateRisk(id: string, data: any) {
  const response = await api.put(`/risks/${id}`, data);
  return response.data;
}

export async function deleteRisk(id: string) {
  const response = await api.delete(`/risks/${id}`);
  return response.data;
}
