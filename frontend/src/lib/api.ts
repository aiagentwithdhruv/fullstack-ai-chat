import { Conversation, ConversationList, Message } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

// --- Conversations ---

export async function listConversations(): Promise<ConversationList> {
  return apiFetch("/api/conversations");
}

export async function getConversation(id: string): Promise<Conversation> {
  return apiFetch(`/api/conversations/${id}`);
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  return apiFetch(`/api/conversations/${conversationId}/messages`);
}

export async function deleteConversation(id: string): Promise<void> {
  await apiFetch(`/api/conversations/${id}`, { method: "DELETE" });
}

// --- Chat ---

export async function sendMessageStream(
  message: string,
  conversationId: string | null,
  files: File[],
  onToken: (token: string) => void,
  onDone: (conversationId: string) => void,
  onError: (error: string) => void,
): Promise<void> {
  const formData = new FormData();
  formData.append("message", message);
  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }
  for (const file of files) {
    formData.append("files", file);
  }

  const res = await fetch(`${API_URL}/api/chat/send`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    onError(err.detail || "Failed to send message");
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    onError("No response stream");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        try {
          const parsed = JSON.parse(data);
          if (parsed.token) {
            onToken(parsed.token);
          } else if (parsed.conversation_id) {
            onDone(parsed.conversation_id);
          } else if (parsed.error) {
            onError(parsed.error);
          }
        } catch {
          // skip unparseable lines
        }
      }
    }
  }
}

// --- Files ---

export function getFileDownloadUrl(fileId: string): string {
  return `${API_URL}/api/files/${fileId}/download`;
}
