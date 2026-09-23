from fastapi.staticfiles import StaticFiles

import os
import time
import uuid
import glob
import cv2
import numpy as np

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from inference import (
    detect_image,
    format_detections,
    draw_detections
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="SONAR-AI API",
    description="AI-powered underwater sonar target detection",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEST_IMAGES_DIR = os.path.join(BASE_DIR, "test_images")

os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_DIR),
    name="outputs"
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "SONAR-AI",
        "model": "GhostVision YOLO26",
        "detector": "Crab-Pot"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# IMAGE ANALYSIS
# ============================================================

@app.post("/api/analyze/image")
async def analyze_image(
    file: UploadFile = File(...)
):

    start_time = time.time()

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/tiff",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        return {
            "success": False,
            "error": "Unsupported image format"
        }

    contents = await file.read()

    image_array = np.frombuffer(
        contents,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return {
            "success": False,
            "error": "Could not decode image"
        }

    height, width = image.shape[:2]

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    detections = detect_image(image)

    formatted = format_detections(
        detections
    )

    # --------------------------------------------------------
    # Annotated image
    # --------------------------------------------------------

    annotated = draw_detections(
        image,
        detections
    )

    filename = f"{uuid.uuid4().hex}.jpg"

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    cv2.imwrite(
        output_path,
        annotated
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    processing_time = time.time() - start_time

    high_risk = sum(
        1
        for d in formatted
        if d["risk"] == "HIGH"
    )

    return {
        "success": True,
        "filename": file.filename,
        "image": {
            "width": width,
            "height": height
        },
        "detections": formatted,
        "summary": {
            "total_targets": len(formatted),
            "high_risk_targets": high_risk,
            "processing_time": round(
                processing_time,
                3
            )
        },
        "annotated_image": (
            f"/outputs/{filename}"
        )
    }


# ============================================================
# DEMO MISSION
# ============================================================

@app.post("/api/analyze/demo-mission")
def analyze_demo_mission():

    mission_start = time.time()

    # --------------------------------------------------------
    # Find real sonar images from GhostVision test_images
    # --------------------------------------------------------

    patterns = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.tif",
        "*.tiff"
    ]

    image_paths = []

    for pattern in patterns:
        image_paths.extend(
            glob.glob(
                os.path.join(
                    TEST_IMAGES_DIR,
                    "**",
                    pattern
                ),
                recursive=True
            )
        )

    image_paths = sorted(image_paths)

    if not image_paths:
        return {
            "success": False,
            "error": (
                "No demo sonar images found. "
                "Place GhostVision test images inside test_images."
            )
        }

    # --------------------------------------------------------
    # Use a manageable mission sample
    # --------------------------------------------------------

    # For the live SIH demo we process the first 20 frames.
    # Increase this later if desired.
    selected_images = image_paths[:20]

    mission_targets = []
    frame_results = []

    total_processing = 0.0

    # --------------------------------------------------------
    # Process each real sonar frame
    # --------------------------------------------------------

    for frame_index, image_path in enumerate(selected_images):

        frame_start = time.time()

        image = cv2.imread(
            image_path,
            cv2.IMREAD_COLOR
        )

        if image is None:
            continue

        height, width = image.shape[:2]

        detections = detect_image(image)

        formatted = format_detections(
            detections
        )

        # ----------------------------------------------------
        # Save annotated frame
        # ----------------------------------------------------

        annotated = draw_detections(
            image,
            detections
        )

        output_filename = (
            f"mission_{uuid.uuid4().hex}.jpg"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            output_filename
        )

        cv2.imwrite(
            output_path,
            annotated
        )

        frame_time = time.time() - frame_start

        total_processing += frame_time

        # ----------------------------------------------------
        # Add targets
        # ----------------------------------------------------

        for target_index, detection in enumerate(formatted):

            confidence = float(
                detection.get("confidence", 0)
            )

            # These coordinates are deliberately labelled
            # simulated/demo coordinates.
            #
            # They are NOT derived from real navigation data.
            x = 12.9716 + (frame_index * 0.0008)
            y = 74.7958 + (target_index * 0.0006)

            mission_targets.append({
                "id": f"T-{len(mission_targets) + 1:03d}",
                "frame": frame_index + 1,
                "label": detection.get(
                    "label",
                    "Crab-Pot"
                ),
                "confidence": confidence,
                "risk": detection.get(
                    "risk",
                    "LOW"
                ),
                "box": detection.get(
                    "box",
                    []
                ),
                "location": {
                    "latitude": round(y, 6),
                    "longitude": round(x, 6),
                    "source": "SIMULATED_DEMO"
                }
            })

        frame_results.append({
            "frame": frame_index + 1,
            "filename": os.path.basename(image_path),
            "width": width,
            "height": height,
            "targets": len(formatted),
            "processing_time": round(
                frame_time,
                3
            ),
            "annotated_image": (
                f"/outputs/{output_filename}"
            )
        })

    # --------------------------------------------------------
    # Mission statistics
    # --------------------------------------------------------

    total_targets = len(mission_targets)

    high_risk_targets = sum(
        1
        for target in mission_targets
        if target["risk"] == "HIGH"
    )

    medium_risk_targets = sum(
        1
        for target in mission_targets
        if target["risk"] == "MEDIUM"
    )

    low_risk_targets = sum(
        1
        for target in mission_targets
        if target["risk"] == "LOW"
    )

    if total_targets > 0:

        average_confidence = sum(
            target["confidence"]
            for target in mission_targets
        ) / total_targets

    else:
        average_confidence = 0.0

    return {
        "success": True,

        "mission": {
            "id": f"DEMO-{uuid.uuid4().hex[:8].upper()}",
            "name": "Ghost Gear Demonstration Mission",
            "source": "GhostVision SSS test frames",
            "mode": "DEMO",
            "location_mode": "SIMULATED"
        },

        "model": {
            "name": "GhostVision YOLO26",
            "detector": "Crab-Pot",
            "inference": "512x512 tiled"
        },

        "summary": {
            "frames_analyzed": len(frame_results),
            "total_targets": total_targets,
            "high_risk_targets": high_risk_targets,
            "medium_risk_targets": medium_risk_targets,
            "low_risk_targets": low_risk_targets,
            "average_confidence": round(
                average_confidence,
                4
            ),
            "processing_time": round(
                total_processing,
                3
            ),
            "mission_time": round(
                time.time() - mission_start,
                3
            )
        },

        "targets": mission_targets,

        "frames": frame_results,

        "notice": (
            "This is a demonstration mission using real "
            "side-scan sonar frames and real YOLO26 inference. "
            "Target coordinates are simulated because the "
            "demo frames are not being georeferenced from "
            "raw sonar navigation metadata."
        )
    }


# ============================================================
# XTF / JSF INGESTION PLACEHOLDER
# ============================================================

@app.post("/api/analyze/mission")
async def analyze_mission(
    file: UploadFile = File(...)
):

    filename = file.filename or ""

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in [".xtf", ".jsf"]:

        return {
            "success": False,
            "error": (
                "Mission files must be XTF or JSF."
            )
        }

    return {
        "success": False,
        "status": "PARSER_NOT_CONNECTED",
        "filename": filename,
        "message": (
            "The XTF/JSF ingestion endpoint is ready, "
            "but raw sonar-log parsing is not connected yet. "
            "Use the Demo Mission workflow for live AI inference."
        )
    }