from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from pypdf import PdfReader
from docx import Document
import uuid

from app.services.rag.knowledge import add_document, delete_document_by_filename

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(filepath))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        doc = Document(str(filepath))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if suffix in [".txt", ".md", ".csv", ".json"]:
        return filepath.read_text(errors="ignore")

    raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")


@router.post("/")
async def upload(file: UploadFile = File(...)):
    safe_name = Path(file.filename).name
    filepath = UPLOAD_DIR / safe_name

    content = await file.read()
    filepath.write_bytes(content)

    text = extract_text(filepath)

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found")

    doc_id = str(uuid.uuid4())

    chunks_indexed = add_document(
        text=text,
        doc_id=doc_id,
        filename=safe_name
    )

    return {
        "success": True,
        "filename": safe_name,
        "doc_id": doc_id,
        "characters_indexed": len(text),
        "chunks_indexed": chunks_indexed
    }


@router.get("/")
def list_uploads():
    files = []

    for path in UPLOAD_DIR.iterdir():
        if path.is_file():
            files.append({
                "filename": path.name,
                "size": path.stat().st_size
            })

    return {
        "files": files
    }


@router.delete("/{filename}")
def delete_upload(filename: str):
    safe_name = Path(filename).name
    filepath = UPLOAD_DIR / safe_name

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    filepath.unlink()

    chunks_deleted = delete_document_by_filename(safe_name)

    return {
        "success": True,
        "deleted": safe_name,
        "chunks_deleted": chunks_deleted
    }


@router.delete("/{filename}")
def delete_upload(filename: str):
    safe_name = Path(filename).name
    filepath = UPLOAD_DIR / safe_name

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    filepath.unlink()

    return {
        "success": True,
        "deleted": safe_name
    }
