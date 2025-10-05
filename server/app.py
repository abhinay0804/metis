import os
import json
import uuid
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from file_processor import FileProcessor
from sensitive_data_masking import SensitiveDataMasker
from .analysis.quality_content_analyzer import QualityContentAnalyzer as DataAnalyzer

from .auth import verify_id_token, User
from .storage import FirestoreStore, LocalMaskedStore, LocalAnalysisStore


app = FastAPI(title="Optiv Masking API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # wildcard origin
    allow_credentials=False,  # must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessResponse(BaseModel):
    masking_id: str
    masked: dict


# Initialize components
processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
masker = SensitiveDataMasker(use_model_detector=True)
analyzer = DataAnalyzer()
# Prefer Firestore; fall back to local masked store if Firestore unavailable
try:
    firestore_store = FirestoreStore()
    _masked_store = firestore_store
except Exception:
    _masked_store = LocalMaskedStore(base_dir=os.path.join(os.getcwd(), "data"))

analysis_store = LocalAnalysisStore(base_dir=os.path.join(os.getcwd(), "data"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/process", response_model=ProcessResponse)
async def process_file(
    file: UploadFile = File(...),
    user: User = Depends(verify_id_token),
):
    # Persist upload to a temp path
    tmp_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    # Extract ORIGINAL (unmasked)
    file_type = processor.get_file_type(tmp_path)
    # Bypass FileProcessor masking to get original content
    # Use processor's internal extractor lookup path
    extractor = processor.extractors.get(file_type)
    if extractor is None:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
    # Some extractors accept flags; use defaults for now
    try:
        if hasattr(extractor, "extract"):
            if file_type == "application/pdf":
                original_content = extractor.extract(tmp_path, enable_ocr=True)
            else:
                original_content = extractor.extract(tmp_path)
        else:
            raise ValueError("Invalid extractor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Mask
    masked_content = masker.mask_sensitive_data(original_content)

    # Create masking record id
    masking_id = str(uuid.uuid4())

    # Save masked to store with metadata
    try:
        _masked_store.save_masked(user.uid, masking_id, {
            "file_name": file.filename,
            "file_type": file_type,
            "masked_content": masked_content,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reversible": False,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save masked data: {str(e)}")

    # Reversible storage disabled
    return ProcessResponse(masking_id=masking_id, masked=masked_content)


@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    user: User = Depends(verify_id_token),
):
    # Save to temp
    tmp_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    file_type = processor.get_file_type(tmp_path)
    extractor = processor.extractors.get(file_type)
    if extractor is None:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
    try:
        if hasattr(extractor, "extract"):
            if file_type == "application/pdf":
                content = extractor.extract(tmp_path, enable_ocr=True)
            else:
                content = extractor.extract(tmp_path)
        else:
            raise ValueError("Invalid extractor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    result = analyzer.analyze(content, file_type)
    # persist analysis record
    analysis_id = str(uuid.uuid4())
    analysis_store.save(user.uid, analysis_id, {
        "file_name": file.filename,
        "file_type": file_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    })
    return {"analysis_id": analysis_id, **result}


class ListItem(BaseModel):
    masking_id: str
    file_name: str
    file_type: str
    created_at: Optional[str] = None
    reversible: Optional[bool] = None

class AnalysisListItem(BaseModel):
    analysis_id: str
    file_name: str
    file_type: str
    created_at: Optional[str] = None


@app.get("/maskings")
def list_maskings(user: User = Depends(verify_id_token)) -> list[ListItem]:
    items = _masked_store.list_maskings(user.uid)
    return [ListItem(**i) for i in items]


@app.get("/maskings/{masking_id}")
def get_masked(masking_id: str, user: User = Depends(verify_id_token)) -> dict:
    doc = _masked_store.get_masked(user.uid, masking_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc


@app.get("/analyses")
def list_analyses(user: User = Depends(verify_id_token)) -> list[AnalysisListItem]:
    items = analysis_store.list(user.uid)
    return [AnalysisListItem(**i) for i in items]


@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: str, user: User = Depends(verify_id_token)) -> dict:
    doc = analysis_store.get(user.uid, analysis_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc




