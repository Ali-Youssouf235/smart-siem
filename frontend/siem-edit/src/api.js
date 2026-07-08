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
  searchByField: async (filters = {}) => {
    // Recherche multi-critères directe (utilisée pour le pivot sur un indicateur précis)
    const response = await api.get('/logs/search', { params: filters });
    return response.data;
  },
  ingestRaw: async (rawLog) => {
    // Petite sécurité : ton FastAPI attend du texte brut ("text/plain") ou un body direct
    const response = await api.post('/logs/ingest/raw', rawLog, {
      headers: { 'Content-Type': 'text/plain' }
    });
    return response.data;
  },
  getTimeline: async (filters = {}) => {
    // { source_ip, host, date_from, date_to } — investigation forensique chronologique
    const response = await api.get('/logs/timeline', { params: filters });
    return response.data; // { total, timeline: [...] }
  },
  toggleSuspect: async (id, isSuspect) => {
    const response = await api.patch(`/logs/${id}/suspect`, { is_suspect: isSuspect });
    return response.data;
  },
  listSuspects: async (size = 100) => {
    const response = await api.get('/logs/suspects', { params: { size } });
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
  listArchive: async (limit = 20) => {
    const response = await api.get('/reports/archive', { params: { limit } });
    return response.data; // { total, reports: [...] }
  },
  downloadArchived: async (id) => {
    const response = await api.get(`/reports/archive/${id}/download`, { responseType: 'blob' });
    return response.data;
  },
  getSchedule: async () => {
    const response = await api.get('/reports/schedule');
    return response.data; // { frequency, hour, last_run }
  },
  setSchedule: async (frequency, hour) => {
    const response = await api.put('/reports/schedule', { frequency, hour });
    return response.data;
  },
};

/* ------------------ 📤 EXPORT CSV / EXCEL (Logs & Alertes) ------------------ */
const triggerBlobDownload = (blobData, filename, mimeType) => {
  const url = window.URL.createObjectURL(new Blob([blobData], { type: mimeType }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const exportApi = {
  exportLogs: async (format, filters = {}) => {
    const response = await api.get('/logs/export', { params: { format, ...filters }, responseType: 'blob' });
    const mime = format === 'xlsx'
      ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      : 'text/csv';
    const ext = format === 'xlsx' ? 'xlsx' : 'csv';
    triggerBlobDownload(response.data, `smart_siem_logs_${Date.now()}.${ext}`, mime);
  },
  exportAlerts: async (format, filters = {}) => {
    const response = await api.get('/alerts/export', { params: { format, ...filters }, responseType: 'blob' });
    const mime = format === 'xlsx'
      ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      : 'text/csv';
    const ext = format === 'xlsx' ? 'xlsx' : 'csv';
    triggerBlobDownload(response.data, `smart_siem_alertes_${Date.now()}.${ext}`, mime);
  },
};

/* ------------------ 📡 AGENTS & CONTEXTE UEBA ------------------ */
export const agentApi = {
  list: async () => {
    const response = await api.get('/agent');
    return response.data;
  },
};

/* ------------------ ⚙️ RÈGLES DE CORRÉLATION (MITRE ATT&CK) ------------------ */
export const rulesApi = {
  list: async () => {
    const response = await api.get('/rules');
    return response.data; // Format attendu : { total_rules: X, rules: [...] }
  },
  create: async (ruleData) => {
    const response = await api.post('/rules', ruleData);
    return response.data;
  },
  update: async (id, ruleData) => {
    const response = await api.put(`/rules/${id}`, ruleData);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/rules/${id}`);
    return response.data;
  },
};

/* ------------------ 🗄️ POLITIQUE DE RÉTENTION DES LOGS ------------------ */
export const retentionApi = {
  get: async () => {
    const response = await api.get('/retention');
    return response.data; // { value, unit, duration_seconds }
  },
  update: async (value, unit) => {
    const response = await api.put('/retention', { value, unit });
    return response.data;
  },
  purgeNow: async () => {
    const response = await api.post('/retention/purge-now');
    return response.data;
  },
};