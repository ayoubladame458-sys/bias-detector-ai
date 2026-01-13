import axios from 'axios';

// Helper function to extract error message from API errors
export function getErrorMessage(err: any, fallback: string = 'An error occurred'): string {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    // Pydantic validation error - extract messages
    return detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(', ');
  } else if (typeof detail === 'string') {
    return detail;
  }
  return err?.message || fallback;
}

import {
  BiasAnalysisResult,
  DocumentUploadResponse,
  DocumentMetadata,
  SearchQuery,
  SearchResponse,
  AnalysisRequest,
  RAGQuestionRequest,
  RAGQuestionResponse,
  SystemStatistics,
  AnalysisHistoryResponse,
  DocumentListResponse,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentsApi = {
  upload: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  list: async (skip = 0, limit = 20): Promise<DocumentListResponse> => {
    const response = await api.get(`/documents/list?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getMetadata: async (documentId: string): Promise<DocumentMetadata> => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  delete: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`);
  },
};

export const analysisApi = {
  analyze: async (request: AnalysisRequest): Promise<BiasAnalysisResult> => {
    const response = await api.post('/analysis/analyze', {
      ...request,
      use_rag: request.use_rag ?? true, // Enable RAG by default
    });
    return response.data;
  },

  getHistory: async (documentId: string, limit = 10): Promise<AnalysisHistoryResponse> => {
    const response = await api.get(`/analysis/history/${documentId}?limit=${limit}`);
    return response.data;
  },

  getLatest: async (documentId: string): Promise<BiasAnalysisResult> => {
    const response = await api.get(`/analysis/latest/${documentId}`);
    return response.data;
  },

  getAll: async (skip = 0, limit = 20) => {
    const response = await api.get(`/analysis/all?skip=${skip}&limit=${limit}`);
    return response.data;
  },
};

export const searchApi = {
  search: async (query: SearchQuery): Promise<SearchResponse> => {
    const response = await api.post('/search', query);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/search/stats');
    return response.data;
  },
};

export const ragApi = {
  askQuestion: async (request: RAGQuestionRequest): Promise<RAGQuestionResponse> => {
    const response = await api.post('/rag/ask', request);
    return response.data;
  },

  getContext: async (text: string, excludeDocId?: string, topK = 5) => {
    const response = await api.post('/rag/context', {
      text,
      exclude_document_id: excludeDocId,
      top_k: topK,
    });
    return response.data;
  },

  getStatistics: async (): Promise<SystemStatistics> => {
    const response = await api.get('/rag/statistics');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/rag/status');
    return response.data;
  },
};

export default api;
