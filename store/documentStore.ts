import { create } from 'zustand';
import { AnalysisResponse, QAItem, StoredDocument } from '../types';

interface DocumentStore {
  documents: StoredDocument[];
  uploadedFilenames: string[]; // Kept for analysis context
  analysisResults: AnalysisResponse | null;
  qaHistory: QAItem[];
  
  setDocuments: (docs: StoredDocument[]) => void;
  addDocument: (doc: StoredDocument) => void;
  
  setUploadedFilenames: (filenames: string[]) => void;
  
  setAnalysisResults: (data: AnalysisResponse) => void;
  
  addQAItem: (item: QAItem) => void;
  clearQAHistory: () => void;
  resetAnalysis: () => void;
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  uploadedFilenames: [],
  analysisResults: null,
  qaHistory: [],

  setDocuments: (docs) => set({ documents: docs }),
  
  addDocument: (doc) => set((state) => ({ 
    documents: [doc, ...state.documents] 
  })),

  setUploadedFilenames: (filenames) => set({ uploadedFilenames: filenames }),

  setAnalysisResults: (data) => set({ analysisResults: data }),

  addQAItem: (item) => set((state) => ({ 
    qaHistory: [item, ...state.qaHistory] 
  })),

  clearQAHistory: () => set({ qaHistory: [] }),
  
  resetAnalysis: () => set({ analysisResults: null, uploadedFilenames: [] }),
}));