"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import api from "@/lib/api";

interface FileStatus {
  name: string;
  doc_id: string;
  status: "queued" | "parsing" | "classifying" | "indexing" | "ready" | "error";
  error?: string;
}

interface StoredDocument {
  doc_id: string;
  filename: string;
  status: string;
  page_count: number;
  chunk_count: number;
  classification?: {
    document_type: string;
    topic: string;
    sensitivity_level: string;
  };
  error?: string;
}

const STATUS_LABELS: Record<string, string> = {
  queued: "⏳ Queued",
  parsing: "📄 Parsing...",
  classifying: "🔍 Classifying...",
  indexing: "🗂️ Indexing...",
  ready: "✅ Ready",
  error: "❌ Error",
};

const STATUS_COLORS: Record<string, string> = {
  queued: "text-gray-400",
  parsing: "text-blue-400",
  classifying: "text-yellow-400",
  indexing: "text-purple-400",
  ready: "text-green-400",
  error: "text-red-400",
};

const SENSITIVITY_COLORS: Record<string, string> = {
  public: "bg-green-900 text-green-300",
  internal: "bg-yellow-900 text-yellow-300",
  confidential: "bg-orange-900 text-orange-300",
  highly_confidential: "bg-red-900 text-red-300",
};

export default function UploadPage() {
  const [uploadingFiles, setUploadingFiles] = useState<FileStatus[]>([]);
  const [storedDocs, setStoredDocs] = useState<StoredDocument[]>([]);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Load stored documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await api.get("/documents");
      setStoredDocs(res.data.documents);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleUpload(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/tiff": [".tiff"],
    },
    multiple: true,
  });

  const handleUpload = async (acceptedFiles: File[]) => {
    setUploading(true);
    const formData = new FormData();
    acceptedFiles.forEach((file) => formData.append("files", file));

    try {
      const res = await api.post("/upload", formData);
      const uploaded: FileStatus[] = res.data.uploaded.map((f: any) => ({
        name: f.filename,
        doc_id: f.doc_id,
        status: "queued",
      }));

      setUploadingFiles((prev) => [...prev, ...uploaded]);
      uploaded.forEach((f) => pollStatus(f.doc_id));
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const pollStatus = (doc_id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/documents/${doc_id}/status`);
        const status = res.data.status;

        setUploadingFiles((prev) =>
          prev.map((f) => (f.doc_id === doc_id ? { ...f, status } : f))
        );

        if (status === "ready" || status === "error") {
          clearInterval(interval);
          // Refresh stored docs list
          fetchDocuments();
          // Remove from uploading list after 3 seconds
          setTimeout(() => {
            setUploadingFiles((prev) =>
              prev.filter((f) => f.doc_id !== doc_id)
            );
          }, 3000);
        }
      } catch {
        clearInterval(interval);
      }
    }, 2000);
  };

  const handleDelete = async (doc_id: string, filename: string) => {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;

    setDeletingId(doc_id);
    try {
      await api.delete(`/documents/${doc_id}`);
      setStoredDocs((prev) => prev.filter((d) => d.doc_id !== doc_id));
    } catch (err) {
      alert("Failed to delete document.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">📁 Bulk Upload</h1>
            <p className="text-gray-400 mt-1">
              Upload PDFs or images to the knowledge base
            </p>
          </div>
          <a href="/" className="text-blue-400 hover:underline text-sm">
            Go to Chatbot →
          </a>
        </div>

        {/* Drop zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors mb-8 ${
            isDragActive
              ? "border-blue-500 bg-blue-950"
              : "border-gray-700 hover:border-gray-500"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-4xl mb-4">☁️</p>
          {isDragActive ? (
            <p className="text-blue-400 text-lg">Drop files here...</p>
          ) : (
            <>
              <p className="text-lg mb-2">Drag and drop files here</p>
              <p className="text-gray-500 text-sm">
                Supports PDF, PNG, JPG, TIFF · Max {20}MB per file
              </p>
            </>
          )}
        </div>

        {uploading && (
          <p className="text-blue-400 text-center mb-4">Uploading...</p>
        )}

        {/* Currently uploading files */}
        {uploadingFiles.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-3 text-gray-300">
              Processing
            </h2>
            <div className="space-y-2">
              {uploadingFiles.map((file) => (
                <div
                  key={file.doc_id}
                  className="bg-gray-900 rounded-lg p-4 flex justify-between items-center"
                >
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-xs text-gray-500 mt-1">{file.doc_id}</p>
                  </div>
                  <span
                    className={`text-sm font-semibold ${STATUS_COLORS[file.status]}`}
                  >
                    {STATUS_LABELS[file.status]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stored documents */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-300">
              Knowledge Base ({storedDocs.length} documents)
            </h2>
            <button
              onClick={fetchDocuments}
              className="text-xs text-gray-500 hover:text-gray-300"
            >
              ↻ Refresh
            </button>
          </div>

          {storedDocs.length === 0 ? (
            <div className="text-center text-gray-600 py-12 border border-gray-800 rounded-xl">
              <p className="text-3xl mb-3">📭</p>
              <p>No documents uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {storedDocs.map((doc) => (
                <div
                  key={doc.doc_id}
                  className="bg-gray-900 rounded-xl p-4 border border-gray-800"
                >
                  <div className="flex justify-between items-start">
                    {/* Left: doc info */}
                    <div className="flex-1 min-w-0 mr-4">
                      <div className="flex items-center gap-3 flex-wrap">
                        <p className="font-semibold truncate">{doc.filename}</p>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[doc.status]}`}
                        >
                          {STATUS_LABELS[doc.status] || doc.status}
                        </span>
                        {doc.classification?.sensitivity_level && (
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              SENSITIVITY_COLORS[
                                doc.classification.sensitivity_level
                              ] || "bg-gray-700 text-gray-300"
                            }`}
                          >
                            {doc.classification.sensitivity_level.replace(
                              "_",
                              " "
                            )}
                          </span>
                        )}
                      </div>

                      {/* Classification info */}
                      {doc.classification && (
                        <div className="mt-2 text-sm text-gray-400 space-y-0.5">
                          <p>
                            <span className="text-gray-500">Type:</span>{" "}
                            {doc.classification.document_type}
                          </p>
                          <p>
                            <span className="text-gray-500">Topic:</span>{" "}
                            {doc.classification.topic}
                          </p>
                        </div>
                      )}

                      {/* Stats */}
                      <div className="mt-2 flex gap-4 text-xs text-gray-600">
                        <span>{doc.page_count} pages</span>
                        <span>{doc.chunk_count} chunks indexed</span>
                      </div>

                      {/* Error */}
                      {doc.error && (
                        <p className="mt-2 text-xs text-red-400">
                          Error: {doc.error}
                        </p>
                      )}
                    </div>

                    {/* Right: delete button */}
                    <button
                      onClick={() => handleDelete(doc.doc_id, doc.filename)}
                      disabled={deletingId === doc.doc_id}
                      className="text-gray-600 hover:text-red-400 transition-colors disabled:opacity-40 text-xl flex-shrink-0"
                      title="Delete document"
                    >
                      {deletingId === doc.doc_id ? "..." : "🗑️"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}