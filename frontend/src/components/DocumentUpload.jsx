import { useState } from 'react';
import { Upload, X, Loader } from 'lucide-react';
import { documentsAPI } from '../services/api';

export default function DocumentUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const processFiles = async (files) => {
    const supportedTypes = ['application/pdf', 'text/plain', 'text/markdown'];

    for (const file of files) {
      if (!supportedTypes.includes(file.type) && !file.name.endsWith('.md')) {
        setMessage(`⚠️ Unsupported file: ${file.name}. Supported: PDF, TXT, Markdown`);
        continue;
      }

      try {
        setLoading(true);
        setMessage(`📤 Uploading ${file.name}...`);

        const response = await documentsAPI.upload(file);
        setMessage(`✅ Uploaded ${file.name}`);

        if (onUploadSuccess) {
          onUploadSuccess(response);
        }

        // Clear message after 3 seconds
        setTimeout(() => setMessage(''), 3000);
      } catch (error) {
        console.error('Upload error:', error);
        setMessage(`❌ Failed to upload ${file.name}`);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    processFiles(files);
  };

  const handleFileInput = (e) => {
    const files = e.currentTarget.files;
    processFiles(files);
  };

  return (
    <div className="w-full">
      <label
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`block border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          accept=".pdf,.txt,.md,.markdown"
          className="hidden"
          disabled={loading}
        />

        <div className="flex flex-col items-center gap-2">
          {loading ? (
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          ) : (
            <Upload className="w-8 h-8 text-gray-400" />
          )}
          <p className="text-sm font-medium text-gray-700">
            Drag and drop your documents here, or click to select
          </p>
          <p className="text-xs text-gray-500">Supported: PDF, TXT, Markdown</p>
        </div>
      </label>

      {message && (
        <div className="mt-3 p-3 bg-gray-100 rounded-lg text-sm text-gray-700 flex items-center justify-between">
          <span>{message}</span>
          <button
            onClick={() => setMessage('')}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
