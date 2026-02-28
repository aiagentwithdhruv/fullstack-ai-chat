from fastapi import APIRouter, HTTPException

from app.services import mongo_service
from app.models.schemas import ConversationResponse, ConversationListResponse, MessageResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _format_conversation(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", "New Chat"),
        "message_count": doc.get("message_count", 0),
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }


def _format_message(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "conversation_id": doc["conversation_id"],
        "role": doc["role"],
        "content": doc["content"],
        "files": doc.get("files", []),
        "token_count": doc.get("token_count", 0),
        "created_at": doc["created_at"],
    }


@router.get("", response_model=ConversationListResponse)
async def list_conversations(skip: int = 0, limit: int = 50):
    convos, total = await mongo_service.list_conversations(skip, limit)
    return {
        "conversations": [_format_conversation(c) for c in convos],
        "total": total,
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    convo = await mongo_service.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    return _format_conversation(convo)


@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str, limit: int = 50):
    convo = await mongo_service.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    messages = await mongo_service.get_messages(conversation_id, limit)
    return [_format_message(m) for m in messages]


@router.patch("/{conversation_id}")
async def update_conversation(conversation_id: str, title: str):
    convo = await mongo_service.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    await mongo_service.update_conversation_title(conversation_id, title)
    return {"status": "updated"}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    convo = await mongo_service.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    await mongo_service.delete_conversation(conversation_id)
    return {"status": "deleted"}
