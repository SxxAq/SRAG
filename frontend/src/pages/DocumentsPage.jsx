import { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';

export default function DocumentsPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Documents</h2>
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* Documents List Section */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Documents</h2>
        <DocumentList refreshTrigger={refreshKey} />
      </div>
    </div>
  );
}
