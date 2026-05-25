from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from sqlalchemy.orm import Session
import uuid

from app.core.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.rag.knowledge import (
    add_document,
    delete_document_by_filename,
    reset_team_knowledge,
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def require_team(user: User) -> str:
    if not user.team:
        raise HTTPException(status_code=403, detail="User is not assigned to a team")
    return user.team.slug


def team_upload_dir(team_slug: str) -> Path:
    path = UPLOAD_DIR / team_slug
    path.mkdir(parents=True, exist_ok=True)
    return path


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


@router.get("/")
def list_uploads(current_user: User = Depends(get_current_user)):
    team_slug = require_team(current_user)
    directory = team_upload_dir(team_slug)

    files = []

    for path in directory.iterdir():
        if path.is_file():
            files.append({
                "filename": path.name,
                "size": path.stat().st_size,
                "team_slug": team_slug,
            })

    return {"files": files}


@router.post("/")
async def upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    team_slug = require_team(current_user)
    directory = team_upload_dir(team_slug)

    safe_name = Path(file.filename).name
    filepath = directory / safe_name

    content = await file.read()
    filepath.write_bytes(content)

    text = extract_text(filepath)

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found")

    doc_id = str(uuid.uuid4())

    chunks_indexed = add_document(
        text=text,
        doc_id=doc_id,
        filename=safe_name,
        team_slug=team_slug,
    )

    return {
        "success": True,
        "filename": safe_name,
        "doc_id": doc_id,
        "team_slug": team_slug,
        "characters_indexed": len(text),
        "chunks_indexed": chunks_indexed,
    }


@router.delete("/{filename}")
def delete_upload(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    team_slug = require_team(current_user)
    safe_name = Path(filename).name
    filepath = team_upload_dir(team_slug) / safe_name

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    filepath.unlink()

    chunks_deleted = delete_document_by_filename(
        safe_name,
        team_slug=team_slug,
    )

    return {
        "success": True,
        "deleted": safe_name,
        "team_slug": team_slug,
        "chunks_deleted": chunks_deleted,
    }


@router.post("/reindex")
def reindex_uploads(current_user: User = Depends(get_current_user)):
    team_slug = require_team(current_user)
    directory = team_upload_dir(team_slug)

    deleted_chunks = reset_team_knowledge(team_slug)

    indexed_files = []
    failed_files = []

    for filepath in directory.iterdir():
        if not filepath.is_file():
            continue

        try:
            text = extract_text(filepath)

            if not text.strip():
                failed_files.append({
                    "filename": filepath.name,
                    "reason": "No extractable text",
                })
                continue

            doc_id = str(uuid.uuid4())

            chunks_indexed = add_document(
                text=text,
                doc_id=doc_id,
                filename=filepath.name,
                team_slug=team_slug,
            )

            indexed_files.append({
                "filename": filepath.name,
                "doc_id": doc_id,
                "chunks_indexed": chunks_indexed,
            })

        except Exception as exc:
            failed_files.append({
                "filename": filepath.name,
                "reason": str(exc),
            })

    return {
        "success": True,
        "team_slug": team_slug,
        "deleted_chunks": deleted_chunks,
        "indexed_files": indexed_files,
        "failed_files": failed_files,
    }
