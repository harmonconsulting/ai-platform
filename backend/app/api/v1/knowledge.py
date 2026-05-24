from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag.knowledge import search

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/search")
def knowledge_search(req: SearchRequest):
    return {
        "query": req.query,
        "results": search(req.query, k=req.k)
    }
