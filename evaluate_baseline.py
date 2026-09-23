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

CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.50

OUTPUT_DIR = Path("outputs/baseline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("LOADING GV-YOLO26")
print("=" * 60)

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


# ============================================================
# IOU
# ============================================================

def calculate_iou(box_a, box_b):

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    intersection_x1 = max(ax1, bx1)
    intersection_y1 = max(ay1, by1)

    intersection_x2 = min(ax2, bx2)
    intersection_y2 = min(ay2, by2)

    intersection_width = max(
        0,
        intersection_x2 - intersection_x1
    )

    intersection_height = max(
        0,
        intersection_y2 - intersection_y1
    )

    intersection_area = (
        intersection_width *
        intersection_height
    )

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union_area = area_a + area_b - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess(image):

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image_resized = cv2.resize(
        image_rgb,
        (640, 640)
    )

    image_input = (
        image_resized.astype(np.float32)
        / 255.0
    )

    image_input = np.transpose(
        image_input,
        (2, 0, 1)
    )

    image_input = np.expand_dims(
        image_input,
        axis=0
    )

    return image_input


# ============================================================
# RUN DETECTION
# ============================================================

def detect(image):

    original_height, original_width = image.shape[:2]

    input_tensor = preprocess(image)

    output = session.run(
        None,
        {
            input_name: input_tensor
        }
    )[0][0]

    detections = []

    for detection in output:

        x1, y1, x2, y2, confidence, class_id = detection

        confidence = float(confidence)

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        # Convert model coordinates back
        # to original image coordinates

        x1 = x1 * original_width / 640
        x2 = x2 * original_width / 640

        y1 = y1 * original_height / 640
        y2 = y2 * original_height / 640

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
# READ GROUND TRUTH
# ============================================================

print("\nReading test annotations...")

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

print("Test images:", len(records))


# ============================================================
# EVALUATION
# ============================================================

true_positives = 0
false_positives = 0
false_negatives = 0

total_ground_truth = 0
total_predictions = 0

processed = 0


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

    ground_truth_boxes = []

    boxes = objects.get(
        "bbox",
        []
    )

    categories = objects.get(
        "category",
        []
    )

    for i, box in enumerate(boxes):

        # Only evaluate confirmed Crab-Pot
        # annotations

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
    # Predictions
    # --------------------------------------------------------

    predictions = detect(image)

    total_ground_truth += len(
        ground_truth_boxes
    )

    total_predictions += len(
        predictions
    )

    # --------------------------------------------------------
    # Match predictions to ground truth
    # --------------------------------------------------------

    matched_ground_truth = set()

    for prediction in sorted(
        predictions,
        key=lambda x: x["confidence"],
        reverse=True
    ):

        best_iou = 0
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

    false_negatives += (
        len(ground_truth_boxes)
        - len(matched_ground_truth)
    )

    processed += 1

    if processed % 25 == 0:

        print(
            f"Processed {processed}/"
            f"{len(records)}"
        )


# ============================================================
# METRICS
# ============================================================

precision = (
    true_positives /
    (true_positives + false_positives)
    if (true_positives + false_positives) > 0
    else 0
)

recall = (
    true_positives /
    (true_positives + false_negatives)
    if (true_positives + false_negatives) > 0
    else 0
)

f1 = (
    2 * precision * recall /
    (precision + recall)
    if (precision + recall) > 0
    else 0
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("GV-YOLO26 BASELINE RESULTS")
print("=" * 60)

print(
    f"\nTest images:       {processed}"
)

print(
    f"Ground-truth pots: {total_ground_truth}"
)

print(
    f"Predictions:       {total_predictions}"
)

print(
    f"\nTrue positives:    {true_positives}"
)

print(
    f"False positives:   {false_positives}"
)

print(
    f"False negatives:   {false_negatives}"
)

print("\n-----------------------------")

print(
    f"Precision:         {precision:.4f}"
)

print(
    f"Recall:            {recall:.4f}"
)

print(
    f"F1 Score:          {f1:.4f}"
)

print("=" * 60)
