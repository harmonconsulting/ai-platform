from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.router import LLMRouter
from app.services.rag.knowledge import search

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    if request.conversation_id:

        conversation = db.query(
            Conversation
        ).filter(
            Conversation.id == request.conversation_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

    else:

        conversation = Conversation(
            user_id=1,
            title=request.message[:40]
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    db.add(user_message)

    context_chunks = search(
        request.message,
        k=5
    )

    context_parts=[]

    for chunk in context_chunks:

        metadata=chunk.get(
            "metadata"
        ) or {}

        filename=metadata.get(
            "filename",
            "unknown"
        )

        chunk_index=metadata.get(
            "chunk_index",
            "?"
        )

        context_parts.append(
            f"Source: {filename} | Chunk: {chunk_index}\n{chunk['content']}"
        )

    context="\n\n".join(
        context_parts
    )

    response_text=LLMRouter.chat(
        provider=request.provider,
        model=request.model,
        message=request.message,
        context=context
    )

    assistant_message=Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text
    )

    db.add(
        assistant_message
    )

    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text
    )


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).order_by(
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
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.id.asc()).all()

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
