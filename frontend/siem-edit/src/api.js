import axios from 'axios';

// URL de base de ton API FastAPI
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour injecter automatiquement le Token JWT dans chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ------------------ 🔐 SERVICES D'AUTHENTIFICATION ------------------ */
export const authApi = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data; // Renvoie les infos utilisateur + token
  },
  logout: () => {
    localStorage.removeItem('token');
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

/* ------------------ 👥 GESTION DES ANALYSTES (Elasticsearch) ------------------ */
export const usersApi = {
  list: async () => {
    const response = await api.get('/users');
    return response.data; // Format attendu: { total_users: X, users: [...] }
  },
  create: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },
  update: async (id, userData) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

/* ------------------ 🛡️ FLUX DES ALERTES SOC ------------------ */
export const alertsApi = {
  list: async (filters = {}) => {
    const response = await api.get('/alerts', { params: filters });
    return response.data; // Liste ou objet contenant les alertes
  },
  getStats: async () => {
    const response = await api.get('/alerts/stats');
    return response.data;
  },
  updateStatus: async (id, status) => {
    const response = await api.patch(`/alerts/${id}`, { status });
    return response.data;
  },
};

/* ------------------ 🔍 EXPLORATEUR DE LOGS & INGESTION ------------------ */
export const logsApi = {
  search: async (query = '') => {
    // On appelle la bonne route de recherche multicritères et on passe 'keyword' au lieu de 'q'
    const response = await api.get('/logs/search', { params: { keyword: query } });
    return response.data;
  },
  ingestRaw: async (rawLog) => {
    // Petite sécurité : ton FastAPI attend du texte brut ("text/plain") ou un body direct
    const response = await api.post('/logs/ingest/raw', rawLog, {
      headers: { 'Content-Type': 'text/plain' }
    });
    return response.data;
  },
};
/* ------------------ 📊 RAPPORTS DE SÉCURITÉ ------------------ */
export const reportsApi = {
  downloadPdf: async () => {
    // Crucial : responseType 'blob' pour télécharger un flux binaire PDF
    const response = await api.get('/reports/generate', { responseType: 'blob' });
    return response.data;
  },
};

/* ------------------ 📡 AGENTS & CONTEXTE UEBA ------------------ */
export const agentApi = {
  list: async () => {
    const response = await api.get('/agent');
    return response.data;
  },
};