'use client';

import React, { useEffect, useState } from 'react';
import { History, FileText, Loader2, ChevronRight, Calendar, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { analysisApi, documentsApi, getErrorMessage } from '@/lib/api';
import { DocumentMetadata, BiasAnalysisResult } from '@/types';

interface HistoryItem {
  document: DocumentMetadata;
  latestAnalysis?: BiasAnalysisResult;
}

interface AnalysisHistoryProps {
  onSelectAnalysis?: (analysis: BiasAnalysisResult) => void;
}

export function AnalysisHistory({ onSelectAnalysis }: AnalysisHistoryProps) {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const docsResponse = await documentsApi.list(0, 20);

      const historyItems: HistoryItem[] = await Promise.all(
        docsResponse.documents.map(async (doc) => {
          try {
            if (doc.analyzed) {
              const analysis = await analysisApi.getLatest(doc.document_id);
              return { document: doc, latestAnalysis: analysis };
            }
          } catch {
            // Document hasn't been analyzed yet
          }
          return { document: doc };
        })
      );

      setHistory(historyItems);
    } catch (err: any) {
      setError(getErrorMessage(err, 'Failed to load history'));
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score <= 0.3) return 'text-green-500';
    if (score <= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score <= 0.3) return 'bg-green-500/10';
    if (score <= 0.6) return 'bg-yellow-500/10';
    return 'bg-red-500/10';
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <History className="w-5 h-5 mr-2" />
          Analysis History
        </CardTitle>
        <CardDescription>
          View previously analyzed documents and their bias scores
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-center py-8 text-destructive">
            <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
            <p>{error}</p>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No documents analyzed yet</p>
            <p className="text-sm">Upload and analyze a document to see it here</p>
          </div>
        ) : (
          <div className="space-y-2">
            {history.map((item) => (
              <div
                key={item.document.document_id}
                onClick={() => item.latestAnalysis && onSelectAnalysis?.(item.latestAnalysis)}
                className={`p-4 border rounded-lg transition-colors ${
                  item.latestAnalysis
                    ? 'cursor-pointer hover:bg-muted/50'
                    : 'opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <div>
                      <p className="font-medium text-sm">{item.document.filename}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        {formatDate(item.document.uploaded_at)}
                        <span className="uppercase">{item.document.file_type}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {item.latestAnalysis ? (
                      <>
                        <div
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBg(
                            item.latestAnalysis.overall_score
                          )} ${getScoreColor(item.latestAnalysis.overall_score)}`}
                        >
                          {(item.latestAnalysis.overall_score * 100).toFixed(0)}%
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      </>
                    ) : (
                      <span className="text-xs text-muted-foreground">Not analyzed</span>
                    )}
                  </div>
                </div>
                {item.latestAnalysis && (
                  <div className="mt-2 pt-2 border-t">
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {item.latestAnalysis.summary}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-muted-foreground">
                        {item.latestAnalysis.bias_instances.length} bias instances found
                      </span>
                      {item.latestAnalysis.rag_metadata?.context_used && (
                        <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                          RAG Enhanced
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
