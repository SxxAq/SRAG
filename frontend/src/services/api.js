import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat operations
export const chatAPI = {
  sendMessage: async (query, topK = 5, scoreThreshold = 0.0) => {
    const response = await api.post('/chat', {
      query,
      top_k: topK,
      score_threshold: scoreThreshold,
    });
    return response.data;
  },

  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get('/chat/history', {
      params: { limit, offset },
    });
    return response.data;
  },

  clearHistory: async () => {
    const response = await api.delete('/chat/history');
    return response.data;
  },
};

// Document operations
export const documentsAPI = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (limit = 50, offset = 0) => {
    const response = await api.get('/documents', {
      params: { limit, offset },
    });
    return response.data;
  },

  delete: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },
};

// System operations
export const systemAPI = {
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },
};

export default api;
