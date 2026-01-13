'use client';

import React, { useState } from 'react';
import { Search, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { searchApi, getErrorMessage } from '@/lib/api';
import { SearchResult } from '@/types';

export function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSearched(true);

    try {
      const response = await searchApi.search({
        query: query.trim(),
        top_k: 10,
      });
      setResults(response.results);
    } catch (err: any) {
      setError(getErrorMessage(err, 'Search failed'));
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Search className="w-5 h-5 mr-2" />
          Semantic Search
        </CardTitle>
        <CardDescription>
          Search across all analyzed documents using AI-powered semantic search
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search for bias patterns, topics, or content..."
            className="flex-1 px-4 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <Button onClick={handleSearch} disabled={loading || !query.trim()}>
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </Button>
        </div>

        {error && (
          <div className="p-3 mb-4 bg-destructive/10 border border-destructive rounded-md text-sm text-destructive">
            {error}
          </div>
        )}

        {searched && !loading && results.length === 0 && !error && (
          <div className="text-center py-8 text-muted-foreground">
            <Search className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No results found for "{query}"</p>
            <p className="text-sm">Try different keywords or analyze more documents</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground mb-3">
              Found {results.length} relevant chunks
            </p>
            {results.map((result, index) => (
              <div
                key={index}
                className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-primary" />
                    <span className="font-medium text-sm">{result.filename}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${getRelevanceColor(result.relevance_score)}`}
                    />
                    <span className="text-xs text-muted-foreground">
                      {(result.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {result.text_chunk}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
