import { useState } from 'react';
import { documentsApi, getErrorMessage } from '@/lib/api';
import { DocumentUploadResponse } from '@/types';

export const useUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedDocument, setUploadedDocument] = useState<DocumentUploadResponse | null>(null);

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      const result = await documentsApi.upload(file);
      setUploadedDocument(result);
      return result;
    } catch (err: any) {
      const errorMessage = getErrorMessage(err, 'Failed to upload file');
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    setUploading(false);
    setError(null);
    setUploadedDocument(null);
  };

  return {
    uploadFile,
    uploading,
    error,
    uploadedDocument,
    reset,
  };
};
