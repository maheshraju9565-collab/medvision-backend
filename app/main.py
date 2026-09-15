from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timezone
import uuid
import time


app = FastAPI(
    title="MedVision AI API",
    version="1.0.0"
)


# Allow the GitHub Pages website to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# In-memory scan database
scans = {}


# Supported medical image formats
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".dcm",
    ".dicom"
}


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "MedVision AI API",
        "status": "running",
        "version": "1.0.0"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "medvision-backend"
    }


# --------------------------------------------------
# UPLOAD SCAN
# --------------------------------------------------

@app.post("/api/scans/upload")
async def upload_scan(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Use JPG, JPEG, PNG, DCM or DICOM."
            )
        )

    # Generate unique scan ID
    scan_id = str(uuid.uuid4())

    # Create server filename
    filename = f"{scan_id}{extension}"

    file_path = UPLOAD_DIR / filename

    # Read file
    contents = await file.read()

    # Maximum 100 MB
    max_size = 100 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File is larger than 100 MB."
        )

    # Save file
    file_path.write_bytes(contents)

    # Store scan information
    scans[scan_id] = {
        "scan_id": scan_id,
        "filename": file.filename,
        "stored_file": str(file_path),
        "uploaded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "uploaded",
        "analysis": None
    }

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "status": "uploaded",
        "message": "Scan uploaded successfully."
    }


# --------------------------------------------------
# START ANALYSIS
# --------------------------------------------------

@app.post("/api/scans/{scan_id}/analyze")
def analyze_scan(
    scan_id: str
):

    # Check scan exists
    if scan_id not in scans:
        raise HTTPException(
            status_code=404,
            detail="Scan not found."
        )

    # Mark as processing
    scans[scan_id]["status"] = "processing"

    # Demo processing delay
    time.sleep(2)

    # ------------------------------------------------
    # DEMO AI RESULT
    # ------------------------------------------------
    #
    # This is NOT a real medical diagnosis.
    # A validated medical AI model will be connected later.
    #

    analysis = {
        "model": "medvision-demo-v1",
        "mode": "simulation",
        "body_region": "unknown",
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

    # Store result
    scans[scan_id]["status"] = "completed"

    scans[scan_id]["analysis"] = analysis

    scans[scan_id]["analyzed_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "scan_id": scan_id,
        "status": "completed",
        "analysis": analysis
    }


# --------------------------------------------------
# GET STATUS
# --------------------------------------------------

@app.get("/api/scans/{scan_id}/status")
def scan_status(
    scan_id: str
):

    if scan_id not in scans:
        raise HTTPException(
            status_code=404,
            detail="Scan not found."
        )

    scan = scans[scan_id]

    return {
        "scan_id": scan_id,
        "status": scan["status"]
    }


# --------------------------------------------------
# GET RESULTS
# --------------------------------------------------

@app.get("/api/scans/{scan_id}/results")
def scan_results(
    scan_id: str
):

    if scan_id not in scans:
        raise HTTPException(
            status_code=404,
            detail="Scan not found."
        )

    scan = scans[scan_id]

    return {
        "scan_id": scan_id,
        "filename": scan["filename"],
        "status": scan["status"],
        "uploaded_at": scan["uploaded_at"],
        "analyzed_at": scan.get(
            "analyzed_at"
        ),
        "analysis": scan["analysis"]
    }
