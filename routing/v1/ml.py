from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.params import Depends

from schemas.clickhouse import AnswerResponse
from services.ml import MlService

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.post(
    "/indexing",
    summary="indexing the docx file",
)
async def indexing(file: UploadFile = File(...), ml_service: MlService = Depends()):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted.")

    ml_service.indexing(file.file)


@router.post(
    "/answer",
    summary="indexing the docx file",
    response_model=AnswerResponse,
)
async def answer(
    question: str = Form(),
    file: Optional[UploadFile] = File(None),
    ml_service: MlService = Depends(),
):
    image = None

    if file:
        image = file.file

    return ml_service.get_answer(question, image)
