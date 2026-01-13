export enum BiasType {
  GENDER = "gender",
  POLITICAL = "political",
  CULTURAL = "cultural",
  CONFIRMATION = "confirmation",
  SELECTION = "selection",
  ANCHORING = "anchoring",
  OTHER = "other",
}

export interface BiasInstance {
  type: BiasType;
  text: string;
  explanation: string;
  severity: number;
  start_position: number;
  end_position: number;
  suggestions?: string;
  seen_in_references?: boolean;
}

export interface RAGMetadata {
  context_used: boolean;
  num_reference_chunks: number;
  reference_documents: string[];
}

export interface BiasAnalysisResult {
  document_id: string;
  overall_score: number;
  bias_instances: BiasInstance[];
  summary: string;
  analyzed_at: string;
  rag_metadata?: RAGMetadata;
  comparative_insights?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
}

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  analyzed: boolean;
  analysis_id?: string;
}

export interface SearchQuery {
  query: string;
  top_k?: number;
  filter?: Record<string, any>;
}

export interface SearchResult {
  document_id: string;
  filename: string;
  text_chunk: string;
  relevance_score: number;
  metadata: Record<string, any>;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total_results: number;
}

export interface AnalysisRequest {
  document_id: string;
  bias_types?: BiasType[];
  use_rag?: boolean;
}

// RAG Q&A Types
export interface RAGQuestionRequest {
  question: string;
  document_id?: string;
  top_k?: number;
}

export interface RAGSource {
  filename: string;
  document_id: string;
  relevance: number;
}

export interface RAGQuestionResponse {
  question: string;
  answer: string;
  sources: RAGSource[];
  num_sources_used: number;
}

// Statistics Types
export interface BiasDistribution {
  type: string;
  count: number;
}

export interface SystemStatistics {
  total_documents: number;
  total_analyses: number;
  average_bias_score: number;
  bias_distribution: BiasDistribution[];
  database_connected: boolean;
  rag_enabled: boolean;
}

// Analysis History Types
export interface AnalysisHistoryItem {
  analysis_id: string;
  document_id: string;
  filename: string;
  overall_score: number;
  summary: string;
  analyzed_at: string;
  bias_instances: BiasInstance[];
  rag_metadata?: RAGMetadata;
}

export interface AnalysisHistoryResponse {
  document_id: string;
  analyses: AnalysisHistoryItem[];
  total_count: number;
}

// Documents List Types
export interface DocumentListResponse {
  documents: DocumentMetadata[];
  skip: number;
  limit: number;
  count: number;
}
