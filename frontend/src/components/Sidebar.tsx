"use client";

import { Conversation } from "@/types";
import { formatTime } from "@/lib/utils";
import { MessageSquarePlus, Trash2, MessageSquare } from "lucide-react";

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: SidebarProps) {
  return (
    <aside className="w-64 h-screen bg-chat-sidebar border-r border-chat-border flex flex-col">
      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNew}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-chat-border hover:bg-chat-hover text-sm text-gray-200 transition-colors"
        >
          <MessageSquarePlus size={16} />
          New Chat
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
        {conversations.map((convo) => (
          <div
            key={convo.id}
            onClick={() => onSelect(convo.id)}
            className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition-colors ${
              activeId === convo.id
                ? "bg-chat-hover text-white"
                : "text-gray-400 hover:bg-chat-hover hover:text-gray-200"
            }`}
          >
            <MessageSquare size={14} className="shrink-0" />
            <span className="flex-1 truncate">{convo.title}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(convo.id);
              }}
              className="opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}

        {conversations.length === 0 && (
          <p className="text-gray-600 text-xs text-center mt-8 px-4">
            No conversations yet. Start a new chat!
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-chat-border">
        <p className="text-[10px] text-gray-600 text-center">
          Conversa AI v1.0 | by AiwithDhruv
        </p>
      </div>
    </aside>
  );
}
