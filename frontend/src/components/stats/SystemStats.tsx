'use client';

import React, { useEffect, useState } from 'react';
import { BarChart3, FileText, Brain, Database, Loader2, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { ragApi, getErrorMessage } from '@/lib/api';
import { SystemStatistics } from '@/types';

export function SystemStats() {
  const [stats, setStats] = useState<SystemStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await ragApi.getStatistics();
      setStats(data);
    } catch (err: any) {
      setError(getErrorMessage(err, 'Failed to load statistics'));
    } finally {
      setLoading(false);
    }
  };

  const getBiasTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      gender: 'bg-pink-500',
      political: 'bg-blue-500',
      cultural: 'bg-orange-500',
      confirmation: 'bg-purple-500',
      selection: 'bg-green-500',
      anchoring: 'bg-yellow-500',
      other: 'bg-gray-500',
    };
    return colors[type.toLowerCase()] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">
            {error || 'Unable to load statistics'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const maxBiasCount = Math.max(...stats.bias_distribution.map((b) => b.count), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          System Statistics
        </CardTitle>
        <CardDescription>
          Overview of bias detection across all analyzed documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <FileText className="w-4 h-4" />
              <span className="text-xs">Documents</span>
            </div>
            <p className="text-2xl font-bold">{stats.total_documents}</p>
          </div>

          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Brain className="w-4 h-4" />
              <span className="text-xs">Analyses</span>
            </div>
            <p className="text-2xl font-bold">{stats.total_analyses}</p>
          </div>

          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <TrendingUp className="w-4 h-4" />
              <span className="text-xs">Avg. Bias Score</span>
            </div>
            <p className="text-2xl font-bold">
              {(stats.average_bias_score * 100).toFixed(0)}%
            </p>
          </div>

          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Database className="w-4 h-4" />
              <span className="text-xs">Status</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  stats.database_connected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm font-medium">
                {stats.database_connected ? 'Connected' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <div
                className={`w-2 h-2 rounded-full ${
                  stats.rag_enabled ? 'bg-green-500' : 'bg-yellow-500'
                }`}
              />
              <span className="text-xs text-muted-foreground">
                RAG {stats.rag_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>

        {/* Bias Distribution */}
        {stats.bias_distribution.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-3">Bias Type Distribution</h4>
            <div className="space-y-2">
              {stats.bias_distribution.map((bias) => (
                <div key={bias.type} className="flex items-center gap-3">
                  <span className="text-xs w-24 capitalize">{bias.type}</span>
                  <div className="flex-1 h-4 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getBiasTypeColor(bias.type)} transition-all duration-500`}
                      style={{
                        width: `${(bias.count / maxBiasCount) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8 text-right">
                    {bias.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {stats.bias_distribution.length === 0 && (
          <div className="text-center py-4 text-muted-foreground">
            <p className="text-sm">No bias data available yet</p>
            <p className="text-xs">Analyze documents to see bias distribution</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
