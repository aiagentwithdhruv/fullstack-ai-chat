from collections.abc import AsyncGenerator
from openai import AsyncOpenAI

from app.config import get_settings
from app.models.schemas import FileType
from app.services.file_processor import image_to_base64

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a helpful AI assistant. You can discuss text, analyze documents, \
describe images, and answer questions about uploaded files. Be concise, accurate, and helpful. \
When analyzing files, reference specific content from them."""


def _build_user_content(
    message: str,
    file_texts: list[tuple[str, str]] | None = None,
    image_data: list[tuple[str, str]] | None = None,
) -> list[dict]:
    """Build multimodal content array for OpenAI API."""
    content = []

    # Add file context
    if file_texts:
        for filename, text in file_texts:
            content.append({
                "type": "text",
                "text": f"[File: {filename}]\n{text}",
            })

    # Add images
    if image_data:
        for _filename, b64_data in image_data:
            content.append({
                "type": "image_url",
                "image_url": {"url": b64_data, "detail": "auto"},
            })

    # Add user message
    content.append({"type": "text", "text": message})
    return content


def build_messages(
    conversation_history: list[dict],
    user_message: str,
    file_texts: list[tuple[str, str]] | None = None,
    image_data: list[tuple[str, str]] | None = None,
) -> list[dict]:
    """Build the full messages array for OpenAI."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last 20 messages for context window)
    for msg in conversation_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Build current user message with files
    user_content = _build_user_content(user_message, file_texts, image_data)
    messages.append({"role": "user", "content": user_content})
    return messages


async def chat_stream(
    conversation_history: list[dict],
    user_message: str,
    file_texts: list[tuple[str, str]] | None = None,
    image_data: list[tuple[str, str]] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens."""
    messages = build_messages(conversation_history, user_message, file_texts, image_data)

    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        stream=True,
        max_tokens=4096,
        temperature=0.7,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def chat_complete(
    conversation_history: list[dict],
    user_message: str,
    file_texts: list[tuple[str, str]] | None = None,
    image_data: list[tuple[str, str]] | None = None,
) -> tuple[str, int]:
    """Non-streaming chat completion. Returns (content, total_tokens)."""
    messages = build_messages(conversation_history, user_message, file_texts, image_data)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        max_tokens=4096,
        temperature=0.7,
    )

    content = response.choices[0].message.content or ""
    total_tokens = response.usage.total_tokens if response.usage else 0
    return content, total_tokens


async def generate_title(first_message: str) -> str:
    """Generate a short title for a conversation based on the first message."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a short title (max 6 words) for a conversation that starts with the following message. Reply with only the title, no quotes."},
            {"role": "user", "content": first_message[:500]},
        ],
        max_tokens=20,
        temperature=0.5,
    )
    return response.choices[0].message.content or "New Chat"
