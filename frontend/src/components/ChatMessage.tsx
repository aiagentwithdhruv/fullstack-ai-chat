"use client";

import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FileMetadata } from "@/types";
import { formatFileSize, getFileIcon } from "@/lib/utils";
import { getFileDownloadUrl } from "@/lib/api";
import { User, Bot, Download } from "lucide-react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  files?: FileMetadata[];
  isStreaming?: boolean;
}

export default function ChatMessage({
  role,
  content,
  files = [],
  isStreaming = false,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-4 py-6 px-4 ${isUser ? "" : "bg-chat-assistant/30"}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? "bg-chat-user" : "bg-emerald-600"
        }`}
      >
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-gray-400 mb-1">
          {isUser ? "You" : "AI Assistant"}
        </p>

        {/* File attachments */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {files.map((file, i) => (
              <div
                key={i}
                className="flex items-center gap-2 px-3 py-1.5 bg-chat-input rounded-lg border border-chat-border text-xs"
              >
                <span>{getFileIcon(file.file_type)}</span>
                <span className="truncate max-w-[150px]">{file.filename}</span>
                <span className="text-gray-500">{formatFileSize(file.size)}</span>
                {file.file_id && (
                  <a
                    href={getFileDownloadUrl(file.file_id)}
                    className="text-blue-400 hover:text-blue-300"
                    download
                  >
                    <Download size={12} />
                  </a>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Message content with markdown */}
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                const inline = !match;
                return inline ? (
                  <code
                    className="bg-chat-input px-1.5 py-0.5 rounded text-sm"
                    {...props}
                  >
                    {children}
                  </code>
                ) : (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    className="rounded-lg !my-3"
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                );
              },
            }}
          >
            {content}
          </ReactMarkdown>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-0.5" />
          )}
        </div>
      </div>
    </div>
  );
}
