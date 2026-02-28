export interface FileMetadata {
  filename: string;
  content_type: string;
  size: number;
  file_type: "pdf" | "docx" | "xlsx" | "image";
  file_id?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  files: FileMetadata[];
  token_count: number;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationList {
  conversations: Conversation[];
  total: number;
}
