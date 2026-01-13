'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { BiasInstance, BiasType } from '@/types';
import { AlertCircle } from 'lucide-react';

interface BiasInstancesListProps {
  instances: BiasInstance[];
}

export const BiasInstancesList: React.FC<BiasInstancesListProps> = ({ instances }) => {
  const getBiasTypeColor = (type: BiasType) => {
    const colors: Record<BiasType, string> = {
      [BiasType.GENDER]: 'bg-purple-100 text-purple-800 border-purple-200',
      [BiasType.POLITICAL]: 'bg-blue-100 text-blue-800 border-blue-200',
      [BiasType.CULTURAL]: 'bg-green-100 text-green-800 border-green-200',
      [BiasType.CONFIRMATION]: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      [BiasType.SELECTION]: 'bg-orange-100 text-orange-800 border-orange-200',
      [BiasType.ANCHORING]: 'bg-pink-100 text-pink-800 border-pink-200',
      [BiasType.OTHER]: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[type];
  };

  const getSeverityColor = (severity: number) => {
    if (severity < 0.3) return 'bg-green-500';
    if (severity < 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (instances.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Bias Instances</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No bias instances detected</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Detected Bias Instances ({instances.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {instances.map((instance, index) => (
            <div
              key={index}
              className="p-4 border rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium border ${getBiasTypeColor(
                    instance.type
                  )}`}
                >
                  {instance.type.toUpperCase()}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-muted-foreground">Severity:</span>
                  <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getSeverityColor(instance.severity)}`}
                      style={{ width: `${instance.severity * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium">
                    {Math.round(instance.severity * 100)}%
                  </span>
                </div>
              </div>

              <div className="mb-2">
                <p className="text-sm font-medium mb-1">Biased Text:</p>
                <blockquote className="pl-4 border-l-2 border-primary italic text-sm text-muted-foreground">
                  "{instance.text}"
                </blockquote>
              </div>

              <div className="mb-2">
                <p className="text-sm font-medium mb-1">Explanation:</p>
                <p className="text-sm text-muted-foreground">{instance.explanation}</p>
              </div>

              {instance.suggestions && (
                <div className="mt-3 p-3 bg-muted rounded-md">
                  <p className="text-sm font-medium mb-1">Suggestions:</p>
                  <p className="text-sm text-muted-foreground">{instance.suggestions}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
