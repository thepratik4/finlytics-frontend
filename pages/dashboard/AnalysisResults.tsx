import React, { useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import ReactMarkdown from 'react-markdown';
import { TrendingUp, TrendingDown, Minus, Info, FileText } from 'lucide-react';
import api from '../../services/api';
import { useDocumentStore } from '../../store/documentStore';
import { Button, Card, CardContent, CardHeader, CardTitle, Badge, Skeleton } from '../../components/ui/Primitives';
import { AnalysisResponse, SentimentData } from '../../types';

export default function AnalysisResults() {
  const navigate = useNavigate();
  const { uploadedFilenames, analysisResults, setAnalysisResults } = useDocumentStore();

  const analyzeMutation = useMutation({
    mutationFn: async (filenames: string[]) => {
      const response = await api.post<AnalysisResponse>('/analysis/analyze', { filenames });
      return response.data;
    },
    onSuccess: (data) => {
      setAnalysisResults(data);
    }
  });

  useEffect(() => {
    if (uploadedFilenames.length > 0 && !analysisResults) {
      analyzeMutation.mutate(uploadedFilenames);
    } else if (uploadedFilenames.length === 0 && !analysisResults) {
      // No files to analyze
      // Optional: redirect back to upload or show empty state
    }
  }, [uploadedFilenames, analysisResults]);

  if (uploadedFilenames.length === 0) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold text-slate-900">No documents to analyze</h2>
        <p className="text-slate-500 mt-2">Upload some files to get started.</p>
        <Button className="mt-4" onClick={() => navigate('/dashboard/upload')}>Go to Upload</Button>
      </div>
    );
  }

  if (analyzeMutation.isPending) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-10">
        <div className="flex items-center justify-center space-x-2 text-primary-600 mb-8">
            <div className="animate-spin h-6 w-6 border-2 border-primary-600 border-t-transparent rounded-full"></div>
            <span className="font-medium">AI is analyzing your documents... This may take a moment.</span>
        </div>
        <Skeleton className="h-64 w-full rounded-xl" />
        <div className="grid md:grid-cols-2 gap-6">
            <Skeleton className="h-48 w-full rounded-xl" />
            <Skeleton className="h-48 w-full rounded-xl" />
        </div>
      </div>
    );
  }

  if (analyzeMutation.isError) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-500 text-lg mb-4">An error occurred during analysis.</div>
        <Button onClick={() => analyzeMutation.mutate(uploadedFilenames)}>Retry Analysis</Button>
      </div>
    );
  }

  const data = analysisResults?.analysis;
  if (!data) return null;

  // Prepare chart data
  const chartData = (Object.entries(data.sentiment_analysis) as [string, SentimentData][]).map(([filename, sentiment]) => ({
    name: filename.length > 15 ? filename.substring(0, 15) + '...' : filename,
    polarity: sentiment.polarity,
    subjectivity: sentiment.subjectivity,
    fullFilename: filename
  }));

  const getSentimentColor = (polarity: number) => {
    if (polarity > 0.2) return '#10b981'; // green
    if (polarity < -0.2) return '#ef4444'; // red
    return '#f59e0b'; // yellow/amber
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'Positive': return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'Negative': return <TrendingDown className="h-5 w-5 text-red-500" />;
      default: return <Minus className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-10">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Analysis Results</h1>
        <Button variant="outline" size="sm" onClick={() => navigate('/dashboard/qa')}>Ask Questions</Button>
      </div>

      {/* Overall Summary if multiple files */}
      {data.overall_sentiment && (
        <Card className="bg-slate-900 text-white border-slate-800">
          <CardHeader>
            <CardTitle>Executive Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="bg-slate-800 p-4 rounded-lg">
                    <p className="text-slate-400 text-sm">Avg Polarity</p>
                    <p className={`text-2xl font-bold ${data.overall_sentiment.average_polarity > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {data.overall_sentiment.average_polarity.toFixed(2)}
                    </p>
                </div>
                <div className="bg-slate-800 p-4 rounded-lg">
                    <p className="text-slate-400 text-sm">Total Positive Signals</p>
                    <p className="text-2xl font-bold text-green-400">{data.overall_sentiment.total_positive}</p>
                </div>
                <div className="bg-slate-800 p-4 rounded-lg">
                    <p className="text-slate-400 text-sm">Total Negative Signals</p>
                    <p className="text-2xl font-bold text-red-400">{data.overall_sentiment.total_negative}</p>
                </div>
            </div>
            <p className="text-slate-300 leading-relaxed">{data.overall_sentiment.summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Sentiment Chart */}
      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
            <CardHeader>
                <CardTitle>Sentiment Polarity Overview</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                            <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[-1, 1]} />
                            <Tooltip 
                                cursor={{ fill: '#f1f5f9' }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            <Bar dataKey="polarity" radius={[4, 4, 0, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={getSentimentColor(entry.polarity)} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>

        {/* Legend / Quick Stats */}
        <Card>
            <CardHeader>
                <CardTitle>Analysis Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-500">Subjectivity Score</span>
                    <Info className="h-4 w-4 text-slate-400" />
                </div>
                <div className="space-y-2">
                    {chartData.map((item, i) => (
                        <div key={i} className="flex justify-between items-center text-sm">
                            <span className="truncate w-32">{item.name}</span>
                            <div className="w-24 bg-gray-100 rounded-full h-2">
                                <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${item.subjectivity * 100}%` }}></div>
                            </div>
                            <span className="text-xs font-mono">{item.subjectivity.toFixed(2)}</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
      </div>

      {/* Individual Document Details */}
      <h2 className="text-xl font-bold text-slate-900 mt-8">Document Analysis</h2>
      <div className="grid gap-6">
        {Object.entries(data.individual_analysis).map(([filename, analysisText]) => {
            const sentiment = data.sentiment_analysis[filename];
            return (
                <Card key={filename} className="overflow-hidden">
                    <CardHeader className="bg-slate-50 border-b border-gray-100 flex flex-row items-center justify-between">
                        <div className="flex items-center gap-2">
                            <FileText className="h-5 w-5 text-primary-500" />
                            <CardTitle className="text-lg">{filename}</CardTitle>
                        </div>
                        <div className="flex items-center gap-3">
                            <Badge variant={sentiment.sentiment === 'Positive' ? 'success' : sentiment.sentiment === 'Negative' ? 'danger' : 'warning'}>
                                {sentiment.sentiment}
                            </Badge>
                            {getSentimentIcon(sentiment.sentiment)}
                        </div>
                    </CardHeader>
                    <CardContent className="p-6 grid lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 prose prose-sm prose-slate max-w-none">
                            <h4 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-2">Key Findings</h4>
                            <ReactMarkdown>{analysisText}</ReactMarkdown>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-5 space-y-6 h-fit">
                            <div>
                                <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Interpretation</h5>
                                <p className="text-sm text-slate-700 italic">"{sentiment.interpretation}"</p>
                            </div>
                            
                            {sentiment.positive_signals.length > 0 && (
                                <div>
                                    <h5 className="text-xs font-semibold text-green-600 uppercase tracking-wider mb-2">Positive Signals</h5>
                                    <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                        {sentiment.positive_signals.map((signal, idx) => (
                                            <li key={idx}>{signal}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {sentiment.negative_signals.length > 0 && (
                                <div>
                                    <h5 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-2">Negative Signals</h5>
                                    <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                        {sentiment.negative_signals.map((signal, idx) => (
                                            <li key={idx}>{signal}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            );
        })}
      </div>
    </div>
  );
}