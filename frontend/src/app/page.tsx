"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import ChatInput from "@/components/ChatInput";
import {
  listConversations,
  getMessages,
  deleteConversation,
  sendMessageStream,
} from "@/lib/api";
import { Conversation, Message } from "@/types";

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");

  // Load conversations
  const loadConversations = useCallback(async () => {
    try {
      const data = await listConversations();
      setConversations(data.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load messages when conversation changes
  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      return;
    }
    (async () => {
      try {
        const msgs = await getMessages(activeConversationId);
        setMessages(msgs);
      } catch (err) {
        console.error("Failed to load messages:", err);
      }
    })();
  }, [activeConversationId]);

  // New chat
  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setStreamingContent("");
  };

  // Select conversation
  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
    setStreamingContent("");
  };

  // Delete conversation
  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      if (activeConversationId === id) {
        handleNewChat();
      }
      await loadConversations();
    } catch (err) {
      console.error("Failed to delete:", err);
    }
  };

  // Send message
  const handleSend = async (message: string, files: File[]) => {
    if (isStreaming) return;

    // Optimistic UI — add user message immediately
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId || "",
      role: "user",
      content: message,
      files: files.map((f) => ({
        filename: f.name,
        content_type: f.type,
        size: f.size,
        file_type: f.type.startsWith("image/")
          ? "image"
          : f.name.endsWith(".pdf")
            ? "pdf"
            : f.name.endsWith(".docx")
              ? "docx"
              : "xlsx",
      })),
      token_count: 0,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsStreaming(true);
    setStreamingContent("");

    try {
      await sendMessageStream(
        message,
        activeConversationId,
        files,
        // onToken
        (token) => {
          setStreamingContent((prev) => prev + token);
        },
        // onDone
        async (conversationId) => {
          setActiveConversationId(conversationId);
          setIsStreaming(false);
          setStreamingContent("");
          // Reload messages and conversations
          const msgs = await getMessages(conversationId);
          setMessages(msgs);
          await loadConversations();
        },
        // onError
        (error) => {
          console.error("Stream error:", error);
          setIsStreaming(false);
          setStreamingContent("");
          // Add error message
          setMessages((prev) => [
            ...prev,
            {
              id: `error-${Date.now()}`,
              conversation_id: activeConversationId || "",
              role: "assistant",
              content: `Sorry, an error occurred: ${error}`,
              files: [],
              token_count: 0,
              created_at: new Date().toISOString(),
            },
          ]);
        },
      );
    } catch (err) {
      setIsStreaming(false);
      setStreamingContent("");
      console.error("Send failed:", err);
    }
  };

  return (
    <div className="flex h-screen bg-chat-bg text-white">
      <Sidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={handleSelectConversation}
        onNew={handleNewChat}
        onDelete={handleDeleteConversation}
      />

      <main className="flex-1 flex flex-col">
        <ChatArea
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
        />
        <ChatInput onSend={handleSend} disabled={isStreaming} />
      </main>
    </div>
  );
}
