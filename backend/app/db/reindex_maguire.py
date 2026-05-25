from pathlib import Path
from app.services.rag.knowledge import add_document

UPLOAD_DIR = Path("./uploads")

for file in UPLOAD_DIR.glob("*"):
    try:
        text = file.read_text(errors="ignore")

        add_document(
            text=text,
            doc_id=file.stem,
            filename=file.name,
            team_slug="maguire-eminentdomain"
        )

        print("Indexed:", file.name)

    except Exception as e:
        print("Failed:", file.name, e)
