from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.router import LLMRouter
from app.services.rag.knowledge import search

router = APIRouter()


def build_context(message: str, team_slug: str) -> str:
    context_chunks = search(message, k=5, team_slug=team_slug)

    parts = []

    for chunk in context_chunks:
        metadata = chunk.get("metadata") or {}

        filename = metadata.get("filename", "unknown")
        chunk_index = metadata.get("chunk_index", "?")

        parts.append(
            f"Source: {filename} | Chunk: {chunk_index}\n{chunk['content']}"
        )

    return "\n\n".join(parts)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:40]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    db.add(Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    ))

    context = build_context(request.message, current_user.team.slug if current_user.team else 'global')

    response_text = LLMRouter.chat(
        provider=request.provider,
        model=request.model,
        message=request.message,
        context=context
    )

    db.add(Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text
    ))

    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text
    )


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(
        Conversation.id.desc()
    ).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "user_id": c.user_id,
            "created_at": str(getattr(c, "created_at", "")),
            "updated_at": str(getattr(c, "updated_at", ""))
        }
        for c in conversations
    ]


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.id.asc()
    ).all()

    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": str(getattr(m, "created_at", ""))
            }
            for m in messages
        ]
    }
