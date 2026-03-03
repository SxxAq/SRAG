import { useState, useEffect } from 'react';
import { Loader } from 'lucide-react';
import { systemAPI } from '../services/api';

export default function SettingsPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState({
    topK: 5,
    scoreThreshold: 0.0,
  });

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await systemAPI.getStatus();
      setStatus(response);
    } catch (error) {
      console.error('Error loading status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Status */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">API Status</p>
            <p className="text-lg font-semibold text-green-600">
              {status?.status === 'ready' ? '✓ Ready' : '✗ Down'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Documents Loaded</p>
            <p className="text-lg font-semibold text-gray-900">{status?.documents_loaded || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Embedding Model</p>
            <p className="text-sm text-gray-900 font-mono">{status?.embedding_model}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">LLM Model</p>
            <p className="text-sm text-gray-900 font-mono">{status?.llm_model}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Vector DB</p>
            <p className="text-sm text-gray-900 font-mono">{status?.vector_db}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">API Version</p>
            <p className="text-sm text-gray-900 font-mono">{status?.api_version}</p>
          </div>
        </div>
      </div>

      {/* Retrieval Settings */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Retrieval Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Top K Results
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={config.topK}
              onChange={(e) => setConfig({ ...config, topK: parseInt(e.target.value) })}
              className="input-field w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Number of documents to retrieve for each query (1-20)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Similarity Threshold
            </label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={config.scoreThreshold}
              onChange={(e) => setConfig({ ...config, scoreThreshold: parseFloat(e.target.value) })}
              className="input-field w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Minimum similarity score for relevant documents (0-1)
            </p>
          </div>

          <button className="btn-primary w-full">Save Settings</button>
        </div>
      </div>

      {/* About */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">About SRAG</h3>
        <p className="text-sm text-blue-800">
          Semantic Retrieval-Augmented Generation (SRAG) - Ask questions about your documents
          and get answers powered by state-of-the-art language models.
        </p>
      </div>
    </div>
  );
}
