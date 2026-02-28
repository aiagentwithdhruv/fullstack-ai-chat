"""Basic test to verify imports and app creation."""


def test_app_import():
    from app.main import app
    assert app is not None
    assert app.title == "Full-Stack AI Chat"


def test_config_import():
    from app.config import Settings
    s = Settings(openai_api_key="test")
    assert s.app_name == "Full-Stack AI Chat"
    assert s.max_file_size_mb == 10


def test_file_type_detection():
    from app.services.file_processor import detect_file_type, FileType
    assert detect_file_type("doc.pdf", "application/pdf") == FileType.pdf
    assert detect_file_type("doc.docx", "application/msword") == FileType.docx
    assert detect_file_type("data.xlsx", "application/vnd.ms-excel") == FileType.xlsx
    assert detect_file_type("photo.png", "image/png") == FileType.image
    assert detect_file_type("photo.jpg", "image/jpeg") == FileType.image
