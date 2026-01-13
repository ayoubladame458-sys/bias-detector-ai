'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { BiasAnalysisResult } from '@/types';

interface BiasScoreCardProps {
  result: BiasAnalysisResult;
}

export const BiasScoreCard: React.FC<BiasScoreCardProps> = ({ result }) => {
  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'text-green-600 bg-green-100';
    if (score < 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score < 0.3) return 'Low Bias';
    if (score < 0.6) return 'Moderate Bias';
    return 'High Bias';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Overall Bias Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-center">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="8"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={`${result.overall_score * 251.2} 251.2`}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
                className={getScoreColor(result.overall_score).split(' ')[0]}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="text-3xl font-bold">
                {Math.round(result.overall_score * 100)}
              </span>
              <span className="text-xs text-muted-foreground">/ 100</span>
            </div>
          </div>
        </div>
        <div className="mt-4 text-center">
          <span
            className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(
              result.overall_score
            )}`}
          >
            {getScoreLabel(result.overall_score)}
          </span>
        </div>
        <div className="mt-4 p-4 bg-muted rounded-md">
          <p className="text-sm text-muted-foreground">{result.summary}</p>
        </div>
      </CardContent>
    </Card>
  );
};
