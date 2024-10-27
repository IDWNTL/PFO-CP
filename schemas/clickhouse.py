import uuid
from typing import List, Dict

from pydantic import BaseModel


class CreateChunkOpts(BaseModel):
    id: uuid.UUID
    emb: List[float]
    text: str
    paragraph_id: uuid.UUID


class CreateParagraphOpts(BaseModel):
    id: uuid.UUID
    name: str
    text: str
    num: str
    images: Dict[str, str]


class ParagraphSchema(BaseModel):
    id: uuid.UUID
    name: str
    text: str
    num: str
    images: Dict[str, str]


class ChunkSchema(BaseModel):
    id: uuid.UUID
    emb: List[float] | None
    text: str
    paragraph_id: uuid.UUID


class ChunkWithoutEmb(BaseModel):
    id: uuid.UUID
    text: str
    paragraph_id: uuid.UUID
    cos_dist: float


class AnswerResponse(BaseModel):
    answer: str
    images: list[str]
