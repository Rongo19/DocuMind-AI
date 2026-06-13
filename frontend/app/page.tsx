"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";

interface Citation {
  filename: string;
  page_num: number;
  image_url: string;
  doc_id: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/chat", {
        query: input,
        history: messages,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: res.data.answer,
        citations: res.data.citations,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-800 p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">🧠 Document Intelligence</h1>
        <a href="/upload" className="text-blue-400 text-sm hover:underline">
          Upload Documents →
        </a>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center text-gray-600 mt-24">
            <p className="text-4xl mb-4">💬</p>
            <p className="text-lg">Ask anything about your uploaded documents</p>
            <p className="text-sm mt-2">
              Go to{" "}
              <a href="/upload" className="text-blue-400 hover:underline">
                Upload
              </a>{" "}
              to add documents first
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-5 py-3 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-100"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>

              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 border-t border-gray-700 pt-3">
                  <p className="text-xs text-gray-400 mb-2">Sources:</p>
                  <div className="flex flex-wrap gap-2">
                    {msg.citations.map((c, j) => (
                      <button
                        key={j}
                        onClick={() =>
                          setSelectedImage(
                            `http://localhost:8000${c.image_url}`
                          )
                        }
                        className="bg-gray-700 hover:bg-gray-600 rounded-lg p-2 text-left transition-colors"
                      >
                        <img
                          src={`http://localhost:8000${c.image_url}`}
                          alt={`Page ${c.page_num}`}
                          className="w-16 h-20 object-cover rounded mb-1"
                        />
                        <p className="text-xs text-gray-300 truncate w-16">
                          {c.filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          Page {c.page_num}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-2xl px-5 py-3">
              <p className="text-gray-400 animate-pulse">Thinking...</p>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-4">
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 resize-none outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            Send
          </button>
        </div>
      </div>

      {/* Full page image modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-8"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <img
              src={selectedImage}
              alt="Full page"
              className="max-h-screen object-contain rounded-lg"
            />
            <button
              className="absolute top-2 right-2 bg-gray-800 text-white rounded-full w-8 h-8 flex items-center justify-center"
              onClick={() => setSelectedImage(null)}
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}