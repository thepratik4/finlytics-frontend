import React, { useCallback, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Upload, X, FileText, CheckCircle, AlertCircle, Database, Calendar, HardDrive } from 'lucide-react';
import api from '../../services/api';
import { useDocumentStore } from '../../store/documentStore';
import { Button, Card, CardContent, CardHeader, CardTitle, cn, Badge } from '../../components/ui/Primitives';
import { UploadResponse, DocumentsResponse, StoredDocument } from '../../types';

export default function UploadSection() {
  const navigate = useNavigate();
  const { 
    setUploadedFilenames, 
    setAnalysisResults, 
    documents, 
    setDocuments, 
    addDocument,
    resetAnalysis 
  } = useDocumentStore();
  
  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([]);
  const [selectedStoredDocIds, setSelectedStoredDocIds] = React.useState<Set<string>>(new Set());
  const [uploadError, setUploadError] = React.useState('');
  const [isDragOver, setIsDragOver] = React.useState(false);

  // Fetch stored documents on mount
  const { isLoading: isLoadingDocs, refetch: refetchDocs } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await api.get<DocumentsResponse>('/documents');
      setDocuments(response.data.documents);
      return response.data.documents;
    }
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files[]', file);
      });
      const response = await api.post<UploadResponse>('/analysis/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Add the new simulated files to the store and selection
      data.files.forEach(file => addDocument(file));
      
      // Auto-select the newly uploaded files
      const newIds = new Set(selectedStoredDocIds);
      data.files.forEach(f => newIds.add(f._id));
      setSelectedStoredDocIds(newIds);
      
      setSelectedFiles([]); // Clear upload queue
      refetchDocs(); // Ensure sync
    },
    onError: (error: any) => {
      setUploadError(error.response?.data?.error || 'Upload failed. Please try again.');
    }
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = (Array.from(e.target.files) as File[]).filter(file => file.type === 'application/pdf');
      if (filesArray.length !== e.target.files.length) {
        setUploadError('Only PDF files are allowed.');
      } else {
        setUploadError('');
      }
      setSelectedFiles(prev => [...prev, ...filesArray]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = (Array.from(e.dataTransfer.files) as File[]).filter(file => file.type === 'application/pdf');
    if (files.length === 0) {
      setUploadError('Please drop valid PDF files.');
      return;
    }
    setUploadError('');
    setSelectedFiles(prev => [...prev, ...files]);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleUpload = () => {
    if (selectedFiles.length === 0) return;
    uploadMutation.mutate(selectedFiles);
  };

  const toggleStoredDocSelection = (id: string) => {
    const newSet = new Set(selectedStoredDocIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedStoredDocIds(newSet);
  };

  const handleAnalyzeSelected = () => {
    if (selectedStoredDocIds.size === 0) return;
    
    // Find the filenames of selected docs
    const selectedFilenames = documents
      .filter(doc => selectedStoredDocIds.has(doc._id))
      .map(doc => doc.filename);
      
    // Update store
    resetAnalysis(); // Clear previous results
    setUploadedFilenames(selectedFilenames);
    
    // Navigate
    navigate('/dashboard/results');
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-10">
      <div className="flex justify-between items-center">
        <div>
            <h1 className="text-2xl font-bold text-slate-900">Document Management</h1>
            <p className="text-slate-500">Upload new files or analyze existing documents from your database.</p>
        </div>
      </div>

      {/* Upload Area */}
      <Card>
        <CardContent className="p-8">
          <div 
            className={cn(
              "border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer",
              isDragOver ? "border-primary-500 bg-primary-50" : "border-slate-200 hover:border-primary-400 hover:bg-slate-50"
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <div className="h-12 w-12 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center mb-3">
              <Upload className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Upload New Documents</h3>
            <p className="text-slate-500 text-sm mt-1 max-w-sm">
              Drag & drop PDFs here to save them to the database.
            </p>
            <input 
              id="file-input" 
              type="file" 
              multiple 
              accept=".pdf" 
              className="hidden" 
              onChange={handleFileSelect} 
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="mt-6 space-y-4 border-t border-gray-100 pt-6">
              <div className="flex justify-between items-center">
                  <h4 className="font-medium text-slate-900">Ready to Upload ({selectedFiles.length})</h4>
                  <Button 
                      onClick={handleUpload} 
                      isLoading={uploadMutation.isPending}
                      size="sm"
                  >
                    Save to Database
                  </Button>
              </div>
              <div className="grid gap-2">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg text-sm">
                    <span className="truncate">{file.name}</span>
                    <button onClick={(e) => { e.stopPropagation(); removeFile(idx); }}>
                      <X className="h-4 w-4 text-slate-400 hover:text-red-500" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document Library */}
      <div>
        <div className="flex items-center justify-between mb-4">
             <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary-600" />
                <h2 className="text-xl font-bold text-slate-900">Document Library</h2>
             </div>
             {selectedStoredDocIds.size > 0 && (
                 <Button onClick={handleAnalyzeSelected}>
                    Analyze Selected ({selectedStoredDocIds.size})
                 </Button>
             )}
        </div>

        {isLoadingDocs ? (
            <div className="space-y-3">
                <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
                <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
                <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>
        ) : documents.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                <p className="text-slate-400">No documents in database yet.</p>
            </div>
        ) : (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-100 bg-gray-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <div className="col-span-1 text-center">Select</div>
                    <div className="col-span-5">Filename</div>
                    <div className="col-span-3">Upload Date</div>
                    <div className="col-span-2">Size</div>
                    <div className="col-span-1">Status</div>
                </div>
                <div className="divide-y divide-gray-100">
                    {documents.map((doc) => (
                        <div 
                            key={doc._id} 
                            className={cn(
                                "grid grid-cols-12 gap-4 p-4 items-center hover:bg-blue-50 transition-colors cursor-pointer",
                                selectedStoredDocIds.has(doc._id) && "bg-blue-50"
                            )}
                            onClick={() => toggleStoredDocSelection(doc._id)}
                        >
                            <div className="col-span-1 flex justify-center">
                                <input 
                                    type="checkbox" 
                                    checked={selectedStoredDocIds.has(doc._id)}
                                    onChange={() => {}}
                                    className="h-4 w-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                                />
                            </div>
                            <div className="col-span-5 flex items-center gap-3 overflow-hidden">
                                <FileText className="h-5 w-5 text-slate-400 flex-shrink-0" />
                                <span className="text-sm font-medium text-slate-700 truncate">{doc.filename}</span>
                            </div>
                            <div className="col-span-3 flex items-center gap-2 text-sm text-slate-500">
                                <Calendar className="h-3 w-3" />
                                {new Date(doc.uploadDate).toLocaleDateString()}
                            </div>
                            <div className="col-span-2 text-sm text-slate-500">
                                {(doc.fileSize / 1024 / 1024).toFixed(2)} MB
                            </div>
                            <div className="col-span-1">
                                <Badge variant="success" className="text-[10px]">Stored</Badge>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )}
      </div>
    </div>
  );
}