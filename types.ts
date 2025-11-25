export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  message: string;
  access_token?: string;
  user: User;
  status: number;
}

export interface StoredDocument {
  _id: string;
  filename: string;
  fileSize: number;
  uploadDate: string;
  status: 'uploaded' | 'analyzed' | 'pending';
}

export interface SentimentData {
  polarity: number;
  subjectivity: number;
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  positive_signals: string[];
  negative_signals: string[];
  interpretation: string;
}

export interface IndividualAnalysis {
  filename: string;
  content: string; // The raw text analysis or structured text
}

export interface CombinedAnalysis {
  analysis: string;
  documents_analyzed: string[];
  document_count: number;
}

export interface AnalysisResponse {
  analysis: {
    individual_analysis: Record<string, string>; // filename -> analysis text
    combined_analysis?: CombinedAnalysis;
    sentiment_analysis: Record<string, SentimentData>;
    overall_sentiment?: {
      average_polarity: number;
      average_subjectivity: number;
      total_positive: number;
      total_negative: number;
      summary: string;
    };
  };
  status: number;
}

export interface QAItem {
  id: string;
  question: string;
  response: string;
  timestamp: Date;
  filenames: string[];
}

export interface UploadResponse {
  message: string;
  files: StoredDocument[];
  status: number;
}

export interface DocumentsResponse {
  documents: StoredDocument[];
  status: number;
}