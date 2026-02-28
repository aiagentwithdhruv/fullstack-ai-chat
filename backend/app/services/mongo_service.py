from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId

from app.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db():
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db_name]
    # Create indexes
    await _db.conversations.create_index("created_at")
    await _db.messages.create_index([("conversation_id", 1), ("created_at", 1)])


async def close_db():
    global _client
    if _client:
        _client.close()


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db


async def ping_db() -> bool:
    try:
        if _client is None:
            return False
        await _client.admin.command("ping")
        return True
    except Exception:
        return False


# --- Conversations ---

async def create_conversation(title: str | None = None) -> dict:
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {
        "title": title or "New Chat",
        "message_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.conversations.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get_conversation(conversation_id: str) -> dict | None:
    db = get_db()
    return await db.conversations.find_one({"_id": ObjectId(conversation_id)})


async def list_conversations(skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
    db = get_db()
    total = await db.conversations.count_documents({})
    cursor = db.conversations.find().sort("updated_at", -1).skip(skip).limit(limit)
    convos = await cursor.to_list(length=limit)
    return convos, total


async def update_conversation_title(conversation_id: str, title: str):
    db = get_db()
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"title": title, "updated_at": datetime.now(timezone.utc)}},
    )


async def delete_conversation(conversation_id: str):
    db = get_db()
    oid = ObjectId(conversation_id)
    await db.messages.delete_many({"conversation_id": str(oid)})
    await db.conversations.delete_one({"_id": oid})


# --- Messages ---

async def add_message(
    conversation_id: str,
    role: str,
    content: str,
    files: list[dict] | None = None,
    token_count: int = 0,
) -> dict:
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "files": files or [],
        "token_count": token_count,
        "created_at": now,
    }
    result = await db.messages.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Update conversation
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$inc": {"message_count": 1}, "$set": {"updated_at": now}},
    )
    return doc


async def get_messages(conversation_id: str, limit: int = 50) -> list[dict]:
    db = get_db()
    cursor = (
        db.messages.find({"conversation_id": conversation_id})
        .sort("created_at", 1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


# --- Files ---

async def store_file_metadata(
    conversation_id: str,
    filename: str,
    content_type: str,
    size: int,
    file_type: str,
    extracted_text: str | None = None,
    file_data: bytes | None = None,
) -> str:
    db = get_db()
    doc = {
        "conversation_id": conversation_id,
        "filename": filename,
        "content_type": content_type,
        "size": size,
        "file_type": file_type,
        "extracted_text": extracted_text,
        "created_at": datetime.now(timezone.utc),
    }
    if file_data:
        doc["file_data"] = file_data
    result = await db.files.insert_one(doc)
    return str(result.inserted_id)


async def get_file(file_id: str) -> dict | None:
    db = get_db()
    return await db.files.find_one({"_id": ObjectId(file_id)})
