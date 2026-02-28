import json
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.models.schemas import FileType
from app.services import mongo_service, openai_service, redis_service, file_processor

router = APIRouter(prefix="/api/chat", tags=["chat"])
settings = get_settings()


@router.post("/send")
async def send_message(
    request: Request,
    message: str = Form(...),
    conversation_id: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
):
    """Send a message with optional files, returns SSE stream."""
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not await redis_service.check_rate_limit(client_ip):
        raise HTTPException(429, "Rate limit exceeded. Try again in a minute.")

    # Create or get conversation
    if not conversation_id:
        convo = await mongo_service.create_conversation()
        conversation_id = str(convo["_id"])
    else:
        convo = await mongo_service.get_conversation(conversation_id)
        if not convo:
            raise HTTPException(404, "Conversation not found")

    # Process uploaded files
    file_texts: list[tuple[str, str]] = []
    image_data: list[tuple[str, str]] = []
    file_metadata_list = []

    for f in files:
        if not f.filename:
            continue
        content_bytes = await f.read()

        # Validate size
        if len(content_bytes) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(413, f"File {f.filename} exceeds {settings.max_file_size_mb}MB limit")

        file_type = file_processor.detect_file_type(f.filename, f.content_type or "")

        # Extract text or encode image
        if file_type == FileType.image:
            b64 = file_processor.image_to_base64(content_bytes, f.content_type or "image/png")
            image_data.append((f.filename, b64))
            extracted = None
        else:
            extracted = file_processor.extract_text(content_bytes, file_type)
            if extracted:
                file_texts.append((f.filename, extracted))

        # Store file metadata in DB
        file_id = await mongo_service.store_file_metadata(
            conversation_id=conversation_id,
            filename=f.filename,
            content_type=f.content_type or "",
            size=len(content_bytes),
            file_type=file_type.value,
            extracted_text=extracted,
            file_data=content_bytes,
        )
        file_metadata_list.append({
            "filename": f.filename,
            "content_type": f.content_type or "",
            "size": len(content_bytes),
            "file_type": file_type.value,
            "file_id": file_id,
        })

    # Store user message
    await mongo_service.add_message(
        conversation_id=conversation_id,
        role="user",
        content=message,
        files=file_metadata_list,
    )

    # Get conversation history
    history = await mongo_service.get_messages(conversation_id)

    # Generate title from first message
    if len(history) == 1:
        title = await openai_service.generate_title(message)
        await mongo_service.update_conversation_title(conversation_id, title)

    # Stream response via SSE
    async def event_generator():
        full_response = []
        try:
            async for token in openai_service.chat_stream(
                conversation_history=history[:-1],  # Exclude the message we just added
                user_message=message,
                file_texts=file_texts,
                image_data=image_data,
            ):
                full_response.append(token)
                yield {"event": "token", "data": json.dumps({"token": token})}

            # Store assistant response
            complete_text = "".join(full_response)
            await mongo_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=complete_text,
            )

            yield {
                "event": "done",
                "data": json.dumps({"conversation_id": conversation_id}),
            }
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


@router.post("/send-simple")
async def send_message_simple(
    request: Request,
    message: str = Form(...),
    conversation_id: str | None = Form(None),
):
    """Non-streaming version for simpler clients."""
    client_ip = request.client.host if request.client else "unknown"
    if not await redis_service.check_rate_limit(client_ip):
        raise HTTPException(429, "Rate limit exceeded.")

    if not conversation_id:
        convo = await mongo_service.create_conversation()
        conversation_id = str(convo["_id"])

    await mongo_service.add_message(conversation_id, "user", message)
    history = await mongo_service.get_messages(conversation_id)

    if len(history) == 1:
        title = await openai_service.generate_title(message)
        await mongo_service.update_conversation_title(conversation_id, title)

    content, tokens = await openai_service.chat_complete(
        conversation_history=history[:-1],
        user_message=message,
    )

    await mongo_service.add_message(conversation_id, "assistant", content, token_count=tokens)
    return {"conversation_id": conversation_id, "content": content, "tokens": tokens}
