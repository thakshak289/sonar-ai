import json
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = Path("dataset")
TEST_DIR = DATASET_DIR / "test"
METADATA_FILE = TEST_DIR / "metadata.jsonl"

MODEL_SIZE = 640

# Confidence threshold found from our previous sweep
CONFIDENCE_THRESHOLD = 0.10

# IoU used for evaluation
IOU_THRESHOLD = 0.50

# ------------------------------------------------------------
# TILING SETTINGS
# ------------------------------------------------------------

# For 1024x1024 images this gives:
#
# 0 ---- 512 ---- 1024
# | TILE 1 | TILE 2 |
# |--------|--------|
# | TILE 3 | TILE 4 |
#
TILE_SIZE = 512

# 25% overlap
OVERLAP = 0.25

STRIDE = int(TILE_SIZE * (1 - OVERLAP))

OUTPUT_DIR = Path("outputs/tiled")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 70)
print("LOADING GV-YOLO26")
print("=" * 70)

MODEL_PATH = hf_hub_download(
    repo_id="PINGEcosystem/gv-yolo26",
    filename="weights.onnx"
)

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

print("Model loaded.")
print("Input:", input_name)
print("Input shape:", session.get_inputs()[0].shape)

print()
print("Tile size:", TILE_SIZE)
print("Overlap:", OVERLAP)
print("Stride:", STRIDE)
print("Confidence:", CONFIDENCE_THRESHOLD)


# ============================================================
# IOU
# ============================================================

def calculate_iou(box_a, box_b):

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)

    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(
        0,
        ix2 - ix1
    )

    ih = max(
        0,
        iy2 - iy1
    )

    intersection = iw * ih

    area_a = (
        max(0, ax2 - ax1) *
        max(0, ay2 - ay1)
    )

    area_b = (
        max(0, bx2 - bx1) *
        max(0, by2 - by1)
    )

    union = (
        area_a +
        area_b -
        intersection
    )

    if union <= 0:
        return 0.0

    return intersection / union


# ============================================================
# PREPROCESS
# ============================================================

def preprocess(image):

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    resized = cv2.resize(
        image_rgb,
        (MODEL_SIZE, MODEL_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    tensor = (
        resized.astype(np.float32) /
        255.0
    )

    tensor = np.transpose(
        tensor,
        (2, 0, 1)
    )

    tensor = np.expand_dims(
        tensor,
        axis=0
    )

    return tensor


# ============================================================
# SINGLE TILE DETECTION
# ============================================================

def detect_tile(tile):

    tile_height, tile_width = tile.shape[:2]

    tensor = preprocess(tile)

    output = session.run(
        None,
        {
            input_name: tensor
        }
    )[0][0]

    detections = []

    for detection in output:

        x1, y1, x2, y2, confidence, class_id = detection

        confidence = float(confidence)
        class_id = int(class_id)

        # GhostVision model has Crab-Pot as class 0
        if class_id != 0:
            continue

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        # Convert model coordinates
        # back to tile coordinates

        x1 = x1 * tile_width / MODEL_SIZE
        x2 = x2 * tile_width / MODEL_SIZE

        y1 = y1 * tile_height / MODEL_SIZE
        y2 = y2 * tile_height / MODEL_SIZE

        # Clamp coordinates
        x1 = max(0, min(x1, tile_width))
        x2 = max(0, min(x2, tile_width))

        y1 = max(0, min(y1, tile_height))
        y2 = max(0, min(y2, tile_height))

        # Ignore invalid boxes
        if x2 <= x1 or y2 <= y1:
            continue

        detections.append({
            "box": [
                float(x1),
                float(y1),
                float(x2),
                float(y2)
            ],
            "confidence": confidence
        })

    return detections


# ============================================================
# GENERATE TILES
# ============================================================

def generate_tiles(image):

    height, width = image.shape[:2]

    tiles = []

    # --------------------------------------------------------
    # Special case: image smaller than tile
    # --------------------------------------------------------

    if width <= TILE_SIZE and height <= TILE_SIZE:

        tiles.append({
            "image": image,
            "x_offset": 0,
            "y_offset": 0
        })

        return tiles

    # --------------------------------------------------------
    # X positions
    # --------------------------------------------------------

    x_positions = list(
        range(
            0,
            max(1, width - TILE_SIZE + 1),
            STRIDE
        )
    )

    # Ensure final tile reaches right edge
    if x_positions[-1] + TILE_SIZE < width:

        x_positions.append(
            width - TILE_SIZE
        )

    # --------------------------------------------------------
    # Y positions
    # --------------------------------------------------------

    y_positions = list(
        range(
            0,
            max(1, height - TILE_SIZE + 1),
            STRIDE
        )
    )

    # Ensure final tile reaches bottom edge
    if y_positions[-1] + TILE_SIZE < height:

        y_positions.append(
            height - TILE_SIZE
        )

    # --------------------------------------------------------
    # Create tiles
    # --------------------------------------------------------

    for y in y_positions:

        for x in x_positions:

            x2 = min(
                x + TILE_SIZE,
                width
            )

            y2 = min(
                y + TILE_SIZE,
                height
            )

            tile = image[
                y:y2,
                x:x2
            ]

            tiles.append({
                "image": tile,
                "x_offset": x,
                "y_offset": y
            })

    return tiles


# ============================================================
# NMS
# ============================================================

def non_max_suppression(
    detections,
    iou_threshold=0.50
):

    if not detections:
        return []

    detections = sorted(
        detections,
        key=lambda x: x["confidence"],
        reverse=True
    )

    kept = []

    while detections:

        best = detections.pop(0)

        kept.append(best)

        remaining = []

        for detection in detections:

            iou = calculate_iou(
                best["box"],
                detection["box"]
            )

            if iou < iou_threshold:

                remaining.append(
                    detection
                )

        detections = remaining

    return kept


# ============================================================
# TILED DETECTION
# ============================================================

def detect_tiled(image):

    tiles = generate_tiles(image)

    all_detections = []

    for tile_info in tiles:

        tile = tile_info["image"]

        offset_x = tile_info["x_offset"]
        offset_y = tile_info["y_offset"]

        tile_detections = detect_tile(tile)

        for detection in tile_detections:

            x1, y1, x2, y2 = detection["box"]

            # Convert tile coordinates
            # back to full-image coordinates

            x1 += offset_x
            x2 += offset_x

            y1 += offset_y
            y2 += offset_y

            all_detections.append({
                "box": [
                    x1,
                    y1,
                    x2,
                    y2
                ],
                "confidence": detection["confidence"]
            })

    # --------------------------------------------------------
    # Remove duplicate detections from overlapping tiles
    # --------------------------------------------------------

    final_detections = non_max_suppression(
        all_detections,
        iou_threshold=0.50
    )

    return final_detections


# ============================================================
# READ TEST METADATA
# ============================================================

print()
print("=" * 70)
print("LOADING TEST DATASET")
print("=" * 70)

records = []

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if line:

            records.append(
                json.loads(line)
            )

print(
    "Test images:",
    len(records)
)


# ============================================================
# EVALUATION
# ============================================================

true_positives = 0
false_positives = 0
false_negatives = 0

total_ground_truth = 0
total_predictions = 0

processed = 0


print()
print("=" * 70)
print("RUNNING TILED INFERENCE")
print("=" * 70)


for record in records:

    filename = record["file_name"]

    image_path = TEST_DIR / filename

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        print(
            "WARNING: Could not read",
            image_path
        )

        continue

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    objects = record.get(
        "objects",
        {}
    )

    boxes = objects.get(
        "bbox",
        []
    )

    categories = objects.get(
        "category",
        []
    )

    ground_truth_boxes = []

    for i, box in enumerate(boxes):

        # Only confirmed Crab-Pot
        if i < len(categories):

            if categories[i] != "Crab-Pot":
                continue

        x, y, width, height = box

        ground_truth_boxes.append([
            float(x),
            float(y),
            float(x + width),
            float(y + height)
        ])

    # --------------------------------------------------------
    # TILED PREDICTION
    # --------------------------------------------------------

    predictions = detect_tiled(image)

    total_ground_truth += len(
        ground_truth_boxes
    )

    total_predictions += len(
        predictions
    )

    # --------------------------------------------------------
    # MATCH PREDICTIONS
    # --------------------------------------------------------

    matched_ground_truth = set()

    for prediction in sorted(
        predictions,
        key=lambda x: x["confidence"],
        reverse=True
    ):

        best_iou = 0.0
        best_index = -1

        for i, gt_box in enumerate(
            ground_truth_boxes
        ):

            if i in matched_ground_truth:
                continue

            iou = calculate_iou(
                prediction["box"],
                gt_box
            )

            if iou > best_iou:

                best_iou = iou
                best_index = i

        if best_iou >= IOU_THRESHOLD:

            true_positives += 1

            matched_ground_truth.add(
                best_index
            )

        else:

            false_positives += 1

    # --------------------------------------------------------
    # FALSE NEGATIVES
    # --------------------------------------------------------

    false_negatives += (
        len(ground_truth_boxes)
        -
        len(matched_ground_truth)
    )

    processed += 1

    if processed % 10 == 0:

        print(
            f"Processed "
            f"{processed}/"
            f"{len(records)}"
        )


# ============================================================
# METRICS
# ============================================================

precision = (
    true_positives /
    (true_positives + false_positives)
    if true_positives + false_positives > 0
    else 0
)

recall = (
    true_positives /
    (true_positives + false_negatives)
    if true_positives + false_negatives > 0
    else 0
)

f1 = (
    2 * precision * recall /
    (precision + recall)
    if precision + recall > 0
    else 0
)


# ============================================================
# RESULTS
# ============================================================

print()
print()
print("=" * 70)
print("GV-YOLO26 TILED INFERENCE RESULTS")
print("=" * 70)

print()

print(
    f"Test images:       {processed}"
)

print(
    f"Tile size:         {TILE_SIZE}"
)

print(
    f"Tile overlap:      {OVERLAP * 100:.0f}%"
)

print(
    f"Confidence:        {CONFIDENCE_THRESHOLD}"
)

print(
    f"IoU threshold:     {IOU_THRESHOLD}"
)

print()

print(
    f"Ground-truth pots: {total_ground_truth}"
)

print(
    f"Predictions:       {total_predictions}"
)

print()

print(
    f"True positives:    {true_positives}"
)

print(
    f"False positives:   {false_positives}"
)

print(
    f"False negatives:   {false_negatives}"
)

print()

print(
    "-----------------------------"
)

print(
    f"Precision:         {precision:.4f}"
)

print(
    f"Recall:            {recall:.4f}"
)

print(
    f"F1 Score:          {f1:.4f}"
)

print("=" * 70)

print()
print("Tiled evaluation completed successfully.")