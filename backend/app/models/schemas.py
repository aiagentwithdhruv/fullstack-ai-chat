from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class FileType(str, Enum):
    pdf = "pdf"
    docx = "docx"
    xlsx = "xlsx"
    image = "image"


class FileMetadata(BaseModel):
    filename: str
    content_type: str
    size: int
    file_type: FileType
    extracted_text: str | None = None


class MessageCreate(BaseModel):
    content: str
    conversation_id: str | None = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    files: list[FileMetadata] = []
    token_count: int = 0
    created_at: datetime


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageResponse


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    mongodb: str = "unknown"
    redis: str = "unknown"


class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 500
