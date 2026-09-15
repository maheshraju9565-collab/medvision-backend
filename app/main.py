from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import time

app = FastAPI(
    title="MedVision AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".dcm",
    ".dicom"
}


@app.get("/")
def root():
    return {
        "name": "MedVision AI API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "medvision-backend"
    }


@app.post("/api/scans/upload")
async def upload_scan(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use JPG, JPEG, PNG, DCM or DICOM."
        )

    scan_id = str(uuid.uuid4())

    filename = f"{scan_id}{extension}"
    file_path = UPLOAD_DIR / filename

    contents = await file.read()

    if len(contents) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File is larger than 100 MB."
        )

    file_path.write_bytes(contents)

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "status": "uploaded",
        "message": "Scan uploaded successfully."
    }
@app.post("/api/scans/{scan_id}/analyze")
def analyze_scan(scan_id: str):

    # Demo processing delay
    time.sleep(2)

    return {
        "scan_id": scan_id,
        "status": "completed",
        "analysis": {
            "model": "medvision-demo-v1",
            "mode": "simulation",
            "body_region": "wrist",
            "possible_fracture": None,
            "bone_structure": "requires_ai_model",
            "alignment": "requires_ai_model",
            "confidence": None,
            "message": (
                "This is a prototype integration result. "
                "No clinical diagnosis was performed."
            ),
            "requires_clinician_review": True
        }
    }
