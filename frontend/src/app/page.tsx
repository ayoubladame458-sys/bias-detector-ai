'use client';

import React, { useState, useEffect } from 'react';
import { FileUpload } from '@/components/upload/FileUpload';
import { BiasScoreCard } from '@/components/analysis/BiasScoreCard';
import { BiasInstancesList } from '@/components/analysis/BiasInstancesList';
import { SemanticSearch } from '@/components/search/SemanticSearch';
import { RAGChat } from '@/components/rag/RAGChat';
import { AnalysisHistory } from '@/components/history/AnalysisHistory';
import { SystemStats } from '@/components/stats/SystemStats';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useUpload } from '@/hooks/useUpload';
import { useAnalysis } from '@/hooks/useAnalysis';
import { BiasAnalysisResult } from '@/types';
import {
  Search,
  Upload,
  AlertCircle,
  MessageSquare,
  History,
  BarChart3,
  Brain,
  Sparkles,
  ArrowLeft,
  Shield,
  Zap,
  Database,
  Cpu,
  Lock,
  FileText,
  TrendingUp,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';

type Tab = 'analyze' | 'search' | 'chat' | 'history' | 'stats';

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('analyze');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mounted, setMounted] = useState(false);
  const { uploadFile, uploading, uploadedDocument } = useUpload();
  const { analyzeDocument, analyzing, result, error, setResult } = useAnalysis();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    try {
      const uploadResult = await uploadFile(selectedFile);
      await analyzeDocument({ document_id: uploadResult.document_id, use_rag: true });
    } catch (err) {
      console.error('Error during upload and analysis:', err);
    }
  };

  const handleSelectHistoryAnalysis = (analysis: BiasAnalysisResult) => {
    setResult(analysis);
    setActiveTab('analyze');
  };

  const tabs = [
    { id: 'analyze' as Tab, label: 'Analyze', icon: Upload, description: 'Detect bias in documents' },
    { id: 'search' as Tab, label: 'Search', icon: Search, description: 'Semantic document search' },
    { id: 'chat' as Tab, label: 'RAG Chat', icon: MessageSquare, description: 'AI-powered Q&A' },
    { id: 'history' as Tab, label: 'History', icon: History, description: 'Past analyses' },
    { id: 'stats' as Tab, label: 'Stats', icon: BarChart3, description: 'System metrics' },
  ];

  const features = [
    {
      icon: Cpu,
      title: '100% Local AI',
      description: 'Powered by Ollama - No cloud APIs needed',
      color: 'from-violet-500 to-purple-600'
    },
    {
      icon: Lock,
      title: 'Privacy First',
      description: 'Your data never leaves your machine',
      color: 'from-emerald-500 to-teal-600'
    },
    {
      icon: Database,
      title: 'Vector Search',
      description: 'ChromaDB for semantic understanding',
      color: 'from-blue-500 to-cyan-600'
    },
    {
      icon: Zap,
      title: 'RAG Enhanced',
      description: 'Context-aware intelligent analysis',
      color: 'from-amber-500 to-orange-600'
    }
  ];

  const biasTypes = [
    { name: 'Gender', color: 'bg-pink-500/20 text-pink-400 border-pink-500/30' },
    { name: 'Political', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
    { name: 'Cultural', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
    { name: 'Confirmation', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
    { name: 'Selection', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
    { name: 'Anchoring', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' }
  ];

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/3 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Header */}
      <header className="relative border-b border-white/10 bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Animated Logo */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-primary via-purple-500 to-pink-500 rounded-xl blur-lg opacity-50 animate-pulse" />
                <div className="relative w-12 h-12 rounded-xl bg-gradient-to-br from-primary via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-primary/25">
                  <Brain className="w-7 h-7 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">
                  BiasDetector
                </h1>
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                  100% Local AI - Powered by Ollama
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20">
                <Sparkles className="w-4 h-4 text-primary animate-pulse" />
                <span className="text-sm font-medium text-primary">RAG Enabled</span>
              </div>
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
                <Shield className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-green-500">Private</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="relative border-b border-white/10 bg-background/50 backdrop-blur-lg">
        <div className="container mx-auto px-4">
          <div className="flex gap-1 overflow-x-auto no-scrollbar py-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group relative flex items-center gap-2 px-5 py-3 text-sm font-medium rounded-lg transition-all duration-300 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-primary/20 to-purple-500/20 text-primary shadow-lg shadow-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
                }`}
              >
                <tab.icon className={`w-4 h-4 transition-transform duration-300 ${activeTab === tab.id ? 'scale-110' : 'group-hover:scale-110'}`} />
                <span>{tab.label}</span>
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-gradient-to-r from-primary to-purple-500 rounded-full" />
                )}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative container mx-auto px-4 py-8">
        <div className={`max-w-6xl mx-auto transition-all duration-500 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>

          {/* Analyze Tab */}
          {activeTab === 'analyze' && (
            <div className="slide-up">
              {!result ? (
                <div className="space-y-8">
                  {/* Hero Section */}
                  <div className="text-center space-y-4 py-8">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm text-primary mb-4">
                      <Zap className="w-4 h-4" />
                      <span>AI-Powered Bias Detection</span>
                    </div>
                    <h2 className="text-4xl md:text-5xl font-bold">
                      <span className="gradient-text">Detect Hidden Biases</span>
                      <br />
                      <span className="text-foreground">in Your Documents</span>
                    </h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
                      Upload any document and let our local AI analyze it for various types of cognitive and social biases using RAG-enhanced detection.
                    </p>
                  </div>

                  {/* Features Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {features.map((feature, index) => (
                      <div
                        key={feature.title}
                        className="group relative p-4 rounded-xl bg-card/50 border border-white/10 hover:border-primary/30 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5"
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300`}>
                          <feature.icon className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="font-semibold text-sm mb-1">{feature.title}</h3>
                        <p className="text-xs text-muted-foreground">{feature.description}</p>
                      </div>
                    ))}
                  </div>

                  {/* Upload Section */}
                  <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                    <div className="lg:col-span-3">
                      <Card className="glass-card border-white/10 overflow-hidden">
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-purple-500 to-pink-500" />
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                              <Upload className="w-4 h-4 text-primary" />
                            </div>
                            Upload Document
                          </CardTitle>
                          <CardDescription>
                            Drag and drop or click to select a PDF, TXT, or DOCX file
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <FileUpload onFileSelect={handleFileSelect} />

                          {selectedFile && !analyzing && (
                            <div className="mt-6">
                              <Button
                                onClick={handleUploadAndAnalyze}
                                loading={uploading || analyzing}
                                disabled={!selectedFile}
                                className="w-full h-12 text-base bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 shadow-lg shadow-primary/25 transition-all duration-300 hover:shadow-xl hover:shadow-primary/30"
                              >
                                <Sparkles className="w-5 h-5 mr-2" />
                                {uploading ? 'Uploading...' : 'Analyze with Local AI'}
                              </Button>
                            </div>
                          )}

                          {analyzing && (
                            <div className="mt-6 p-6 rounded-xl bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20">
                              <div className="flex flex-col items-center gap-4">
                                <div className="relative">
                                  <div className="w-16 h-16 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
                                  <Brain className="w-8 h-8 text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                                </div>
                                <div className="text-center">
                                  <p className="font-medium">Analyzing with Ollama...</p>
                                  <p className="text-sm text-muted-foreground">RAG context retrieval in progress</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {error && (
                            <div className="mt-6 p-4 rounded-xl bg-destructive/10 border border-destructive/30">
                              <div className="flex items-center gap-3">
                                <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
                                <p className="text-sm text-destructive">{error}</p>
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>

                    {/* Info Panel */}
                    <div className="lg:col-span-2 space-y-4">
                      <Card className="glass-card border-white/10">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-primary" />
                            Bias Types Detected
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap gap-2">
                            {biasTypes.map((type) => (
                              <span
                                key={type.name}
                                className={`px-3 py-1.5 text-xs font-medium rounded-full border ${type.color} transition-all duration-300 hover:scale-105`}
                              >
                                {type.name}
                              </span>
                            ))}
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="glass-card border-white/10">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base flex items-center gap-2">
                            <FileText className="w-4 h-4 text-primary" />
                            How It Works
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {[
                            { step: '1', text: 'Upload your document' },
                            { step: '2', text: 'RAG retrieves context' },
                            { step: '3', text: 'Ollama analyzes locally' },
                            { step: '4', text: 'Get detailed insights' }
                          ].map((item, i) => (
                            <div key={i} className="flex items-center gap-3 group">
                              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-xs font-bold text-white group-hover:scale-110 transition-transform">
                                {item.step}
                              </div>
                              <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">{item.text}</span>
                            </div>
                          ))}
                        </CardContent>
                      </Card>

                      <Card className="glass-card border-green-500/20 bg-green-500/5">
                        <CardContent className="pt-4">
                          <div className="flex items-start gap-3">
                            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="text-sm font-medium text-green-400">No API Keys Required</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                Everything runs locally on your machine using Ollama and ChromaDB.
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </div>
              ) : (
                /* Results Section */
                <div className="fade-in">
                  <div className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4">
                    <div className="flex items-center gap-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedFile(null);
                          setResult(null);
                        }}
                        className="hover:bg-white/10"
                      >
                        <ArrowLeft className="w-4 h-4 mr-1" />
                        Back
                      </Button>
                      <div>
                        <h2 className="text-2xl font-bold gradient-text">Analysis Results</h2>
                        {result.rag_metadata?.context_used && (
                          <div className="flex items-center gap-2 mt-1">
                            <span className="flex items-center gap-1 text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                              <Sparkles className="w-3 h-3" />
                              RAG Enhanced Analysis
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {result.rag_metadata.num_reference_chunks} references used
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setSelectedFile(null);
                        setResult(null);
                      }}
                      className="border-white/10 hover:bg-white/5"
                    >
                      <ChevronRight className="w-4 h-4 mr-1" />
                      Analyze Another
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1 space-y-4">
                      <BiasScoreCard result={result} />

                      {result.rag_metadata?.context_used && (
                        <Card className="glass-card border-primary/20">
                          <CardHeader className="pb-2">
                            <CardTitle className="text-sm flex items-center gap-2">
                              <Sparkles className="w-4 h-4 text-primary" />
                              RAG Insights
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3 text-sm">
                              <div className="flex justify-between items-center p-2 rounded-lg bg-white/5">
                                <span className="text-muted-foreground">References</span>
                                <span className="font-medium text-primary">{result.rag_metadata.num_reference_chunks}</span>
                              </div>
                              {result.rag_metadata.reference_documents.length > 0 && (
                                <div>
                                  <span className="text-muted-foreground text-xs">Source documents:</span>
                                  <div className="mt-2 flex flex-wrap gap-1">
                                    {result.rag_metadata.reference_documents.map((doc, i) => (
                                      <span key={i} className="text-xs px-2 py-1 bg-white/10 rounded-md border border-white/10">
                                        {doc}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            {result.comparative_insights && (
                              <div className="mt-4 pt-4 border-t border-white/10">
                                <p className="text-xs text-muted-foreground italic">{result.comparative_insights}</p>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      )}
                    </div>

                    <div className="lg:col-span-2">
                      <BiasInstancesList instances={result.bias_instances} />
                    </div>
                  </div>

                  {uploadedDocument && (
                    <div className="mt-6">
                      <Card className="glass-card border-white/10">
                        <CardContent className="pt-6">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
                            <div className="space-y-1">
                              <p className="text-muted-foreground text-xs">Document ID</p>
                              <p className="font-mono text-xs bg-white/5 px-2 py-1 rounded">{uploadedDocument.document_id.slice(0, 12)}...</p>
                            </div>
                            <div className="space-y-1">
                              <p className="text-muted-foreground text-xs">Filename</p>
                              <p className="font-medium truncate">{uploadedDocument.filename}</p>
                            </div>
                            <div className="space-y-1">
                              <p className="text-muted-foreground text-xs">Type</p>
                              <p className="font-medium uppercase text-primary">{uploadedDocument.file_type}</p>
                            </div>
                            <div className="space-y-1">
                              <p className="text-muted-foreground text-xs">Analyzed</p>
                              <p className="font-medium">{new Date(result.analyzed_at).toLocaleString()}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Search Tab */}
          {activeTab === 'search' && (
            <div className="slide-up">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold gradient-text mb-2">Semantic Search</h2>
                <p className="text-muted-foreground">Search your document library using natural language</p>
              </div>
              <SemanticSearch />
            </div>
          )}

          {/* RAG Chat Tab */}
          {activeTab === 'chat' && (
            <div className="slide-up">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold gradient-text mb-2">RAG Chat</h2>
                <p className="text-muted-foreground">Ask questions about bias patterns in your documents</p>
              </div>
              <RAGChat />
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="slide-up">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold gradient-text mb-2">Analysis History</h2>
                <p className="text-muted-foreground">Browse your past document analyses</p>
              </div>
              <AnalysisHistory onSelectAnalysis={handleSelectHistoryAnalysis} />
            </div>
          )}

          {/* Stats Tab */}
          {activeTab === 'stats' && (
            <div className="slide-up">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold gradient-text mb-2">System Statistics</h2>
                <p className="text-muted-foreground">Monitor your BiasDetector usage and performance</p>
              </div>
              <SystemStats />
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-white/10 bg-background/50 backdrop-blur-lg mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-semibold">BiasDetector</p>
                <p className="text-xs text-muted-foreground">100% Local AI Analysis</p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4" />
                <span>Ollama</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                <span>ChromaDB</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                <span>Privacy First</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Built for IA&BD/CCV Specialization
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
