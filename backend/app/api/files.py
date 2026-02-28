from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services import mongo_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/{file_id}")
async def get_file(file_id: str):
    """Get file metadata."""
    file_doc = await mongo_service.get_file(file_id)
    if not file_doc:
        raise HTTPException(404, "File not found")
    return {
        "id": str(file_doc["_id"]),
        "filename": file_doc["filename"],
        "content_type": file_doc["content_type"],
        "size": file_doc["size"],
        "file_type": file_doc["file_type"],
        "has_extracted_text": bool(file_doc.get("extracted_text")),
    }


@router.get("/{file_id}/download")
async def download_file(file_id: str):
    """Download file binary data."""
    file_doc = await mongo_service.get_file(file_id)
    if not file_doc:
        raise HTTPException(404, "File not found")
    if "file_data" not in file_doc:
        raise HTTPException(404, "File data not available")
    return Response(
        content=file_doc["file_data"],
        media_type=file_doc["content_type"],
        headers={"Content-Disposition": f'attachment; filename="{file_doc["filename"]}"'},
    )


@router.get("/{file_id}/text")
async def get_file_text(file_id: str):
    """Get extracted text from a file."""
    file_doc = await mongo_service.get_file(file_id)
    if not file_doc:
        raise HTTPException(404, "File not found")
    return {
        "filename": file_doc["filename"],
        "extracted_text": file_doc.get("extracted_text", ""),
    }
