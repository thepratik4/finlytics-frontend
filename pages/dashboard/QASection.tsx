import React, { useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { Send, User as UserIcon, Bot, Copy, Clock, RefreshCw } from 'lucide-react';
import api from '../../services/api';
import { useDocumentStore } from '../../store/documentStore';
import { Button, Card, CardContent, Input, cn } from '../../components/ui/Primitives';

export default function QASection() {
  const { uploadedFilenames, qaHistory, addQAItem, clearQAHistory } = useDocumentStore();
  const [question, setQuestion] = React.useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const askMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/analysis/ask', {
        question,
        filenames: uploadedFilenames
      });
      return response.data;
    },
    onSuccess: (data) => {
      addQAItem({
        id: Date.now().toString(),
        question,
        response: data.response,
        timestamp: new Date(),
        filenames: uploadedFilenames
      });
      setQuestion('');
    }
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [qaHistory, askMutation.isPending]);

  const handleAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    askMutation.mutate();
  };

  if (uploadedFilenames.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center p-4">
        <div className="bg-slate-100 p-4 rounded-full mb-4">
            <Bot className="h-8 w-8 text-slate-400" />
        </div>
        <h2 className="text-xl font-semibold text-slate-900">No Context Available</h2>
        <p className="text-slate-500 mt-2 max-w-md">Upload documents in the Upload section to start asking questions about your financial data.</p>
      </div>
    );
  }

  // Reverse history for display (newest at bottom is typical chat UI, but state stores newest first usually. Let's handle it)
  // Store adds to front. Chat usually displays oldest to newest top-down.
  const displayHistory = [...qaHistory].reverse();

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
            <h1 className="text-2xl font-bold text-slate-900">Financial Q&A</h1>
            <p className="text-sm text-slate-500">Ask specific questions about the {uploadedFilenames.length} uploaded document(s).</p>
        </div>
        <Button variant="outline" size="sm" onClick={clearQAHistory} disabled={qaHistory.length === 0}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Clear Chat
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden bg-slate-50 border-slate-200 shadow-sm">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-6">
            {displayHistory.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 opacity-60">
                    <Bot className="h-12 w-12 mb-2" />
                    <p>Ask me anything about your documents...</p>
                </div>
            )}
            
            {displayHistory.map((item) => (
                <div key={item.id} className="space-y-4">
                    {/* User Question */}
                    <div className="flex justify-end">
                        <div className="bg-primary-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[85%] shadow-sm">
                            <p className="text-sm">{item.question}</p>
                            <div className="mt-1 text-primary-200 text-[10px] flex justify-end items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </div>
                        </div>
                    </div>

                    {/* AI Response */}
                    <div className="flex justify-start">
                         <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-6 py-4 max-w-[90%] shadow-sm prose prose-sm prose-slate">
                            <div className="flex items-center gap-2 mb-2 border-b border-gray-100 pb-2">
                                <Bot className="h-4 w-4 text-primary-500" />
                                <span className="text-xs font-semibold text-slate-500">Finlytics AI</span>
                            </div>
                            <ReactMarkdown>{item.response}</ReactMarkdown>
                         </div>
                    </div>
                </div>
            ))}

            {askMutation.isPending && (
                <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm flex items-center gap-2">
                        <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                        </div>
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
        </CardContent>

        <div className="p-4 bg-white border-t border-gray-200">
            <form onSubmit={handleAsk} className="flex gap-2">
                <Input 
                    placeholder="E.g., What is the net income growth compared to last year?" 
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="flex-1"
                    disabled={askMutation.isPending}
                />
                <Button type="submit" disabled={askMutation.isPending || !question.trim()}>
                    <Send className="h-4 w-4" />
                </Button>
            </form>
        </div>
      </Card>
    </div>
  );
}