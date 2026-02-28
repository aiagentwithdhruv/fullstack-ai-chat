"use client";

import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import { Message } from "@/types";
import { Bot } from "lucide-react";

interface ChatAreaProps {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
}

export default function ChatArea({
  messages,
  streamingContent,
  isStreaming,
}: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-4">
            <Bot size={32} className="text-emerald-400" />
          </div>
          <h2 className="text-xl font-semibold text-gray-200 mb-2">
            How can I help you today?
          </h2>
          <p className="text-gray-500 text-sm max-w-md">
            Send a message or upload files (PDF, Word, Excel, Images) to start
            a conversation.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            role={msg.role as "user" | "assistant"}
            content={msg.content}
            files={msg.files}
          />
        ))}

        {isStreaming && (
          <ChatMessage
            role="assistant"
            content={streamingContent}
            isStreaming
          />
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
