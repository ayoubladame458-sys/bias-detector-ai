import { useState } from 'react';
import { analysisApi, getErrorMessage } from '@/lib/api';
import { AnalysisRequest, BiasAnalysisResult } from '@/types';

export const useAnalysis = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BiasAnalysisResult | null>(null);

  const analyzeDocument = async (request: AnalysisRequest) => {
    setAnalyzing(true);
    setError(null);

    try {
      const analysisResult = await analysisApi.analyze(request);
      setResult(analysisResult);
      return analysisResult;
    } catch (err: any) {
      const errorMessage = getErrorMessage(err, 'Failed to analyze document');
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    setAnalyzing(false);
    setError(null);
    setResult(null);
  };

  return {
    analyzeDocument,
    analyzing,
    error,
    result,
    setResult,
    reset,
  };
};
