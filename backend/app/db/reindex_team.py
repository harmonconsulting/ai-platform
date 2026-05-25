from pathlib import Path
from app.services.rag.knowledge import add_document
from app.api.v1.upload import extract_text

TEAM_SLUG = "maguire-eminentdomain"
UPLOAD_DIR = Path("./uploads") / TEAM_SLUG

for file in UPLOAD_DIR.glob("*"):
    try:
        text = extract_text(file)

        chunks = add_document(
            text=text,
            doc_id=file.stem,
            filename=file.name,
            team_slug=TEAM_SLUG,
        )

        print("Indexed:", file.name, chunks)

    except Exception as e:
        print("Failed:", file.name, e)
