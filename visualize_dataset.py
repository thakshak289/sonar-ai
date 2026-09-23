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

CONFIDENCE_THRESHOLD = 0.10
IOU_THRESHOLD = 0.50

OUTPUT_DIR = Path("outputs/analysis")

TRUE_POSITIVE_DIR = OUTPUT_DIR / "true_positives"
FALSE_POSITIVE_DIR = OUTPUT_DIR / "false_positives"
FALSE_NEGATIVE_DIR = OUTPUT_DIR / "false_negatives"

TRUE_POSITIVE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FALSE_POSITIVE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FALSE_NEGATIVE_DIR.mkdir(
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

    area_a = (
        max(0, ax2 - ax1) *
        max(0, ay2 - ay1)
    )

    area_b = (
        max(0, bx2 - bx1) *
        max(0, by2 - by1)
    )

    union_area = (
        area_a +
        area_b -
        intersection_area
    )

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
# DETECTION
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

        # Only Crab-Pot class
        if int(class_id) != 0:
            continue

        # Confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        # Convert model coordinates
        # back to original image coordinates

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
# DRAW GROUND TRUTH
# ============================================================

def draw_ground_truth(
    image,
    ground_truth_boxes
):

    for index, box in enumerate(
        ground_truth_boxes
    ):

        x1, y1, x2, y2 = [
            int(value)
            for value in box
        ]

        # Green = ground truth
        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            image,
            "GT",
            (x1, max(20, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2
        )


# ============================================================
# DRAW TP
# ============================================================

def draw_true_positive(
    image,
    box,
    confidence,
    iou
):

    x1, y1, x2, y2 = [
        int(value)
        for value in box
    ]

    # Blue = true positive
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (255, 0, 0),
        3
    )

    label = (
        f"TP {confidence:.2f} "
        f"IoU:{iou:.2f}"
    )

    cv2.putText(
        image,
        label,
        (x1, max(20, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 0, 0),
        2
    )


# ============================================================
# DRAW FP
# ============================================================

def draw_false_positive(
    image,
    box,
    confidence
):

    x1, y1, x2, y2 = [
        int(value)
        for value in box
    ]

    # Red = false positive
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 0, 255),
        3
    )

    label = (
        f"FP {confidence:.2f}"
    )

    cv2.putText(
        image,
        label,
        (x1, max(20, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 255),
        2
    )


# ============================================================
# DRAW FALSE NEGATIVE
# ============================================================

def draw_false_negative(
    image,
    box
):

    x1, y1, x2, y2 = [
        int(value)
        for value in box
    ]

    # Orange = missed ground truth
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 165, 255),
        3
    )

    cv2.putText(
        image,
        "FN - MISSED",
        (x1, max(20, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 165, 255),
        2
    )


# ============================================================
# READ METADATA
# ============================================================

print()
print("=" * 70)
print("READING TEST DATA")
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
# STATISTICS
# ============================================================

total_tp = 0
total_fp = 0
total_fn = 0

processed = 0


# ============================================================
# PROCESS DATASET
# ============================================================

print()
print("=" * 70)
print("ANALYZING PREDICTIONS")
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

    # --------------------------------------------------------
    # Match predictions
    # --------------------------------------------------------

    matched_ground_truth = set()

    true_positive_predictions = []

    false_positive_predictions = []

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

        # ----------------------------------------------------
        # True positive
        # ----------------------------------------------------

        if best_iou >= IOU_THRESHOLD:

            true_positive_predictions.append({
                "box": prediction["box"],
                "confidence": prediction["confidence"],
                "iou": best_iou
            })

            matched_ground_truth.add(
                best_index
            )

            total_tp += 1

        # ----------------------------------------------------
        # False positive
        # ----------------------------------------------------

        else:

            false_positive_predictions.append(
                prediction
            )

            total_fp += 1

    # --------------------------------------------------------
    # False negatives
    # --------------------------------------------------------

    false_negative_boxes = []

    for i, gt_box in enumerate(
        ground_truth_boxes
    ):

        if i not in matched_ground_truth:

            false_negative_boxes.append(
                gt_box
            )

            total_fn += 1

    # ========================================================
    # CREATE ANNOTATED IMAGE
    # ========================================================

    annotated = image.copy()

    # Draw all ground truth boxes first
    draw_ground_truth(
        annotated,
        ground_truth_boxes
    )

    # Draw true positives
    for prediction in true_positive_predictions:

        draw_true_positive(
            annotated,
            prediction["box"],
            prediction["confidence"],
            prediction["iou"]
        )

    # Draw false positives
    for prediction in false_positive_predictions:

        draw_false_positive(
            annotated,
            prediction["box"],
            prediction["confidence"]
        )

    # Draw false negatives
    for box in false_negative_boxes:

        draw_false_negative(
            annotated,
            box
        )

    # ========================================================
    # ADD SUMMARY TO IMAGE
    # ========================================================

    image_tp = len(
        true_positive_predictions
    )

    image_fp = len(
        false_positive_predictions
    )

    image_fn = len(
        false_negative_boxes
    )

    summary = (
        f"TP:{image_tp}  "
        f"FP:{image_fp}  "
        f"FN:{image_fn}"
    )

    cv2.rectangle(
        annotated,
        (5, 5),
        (300, 40),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        annotated,
        summary,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    # ========================================================
    # SAVE TO RELEVANT FOLDERS
    # ========================================================

    output_filename = (
        Path(filename).stem +
        "_analysis.jpg"
    )

    # --------------------------------------------------------
    # Images containing at least one TP
    # --------------------------------------------------------

    if image_tp > 0:

        cv2.imwrite(
            str(
                TRUE_POSITIVE_DIR /
                output_filename
            ),
            annotated
        )

    # --------------------------------------------------------
    # Images containing at least one FP
    # --------------------------------------------------------

    if image_fp > 0:

        cv2.imwrite(
            str(
                FALSE_POSITIVE_DIR /
                output_filename
            ),
            annotated
        )

    # --------------------------------------------------------
    # Images containing at least one FN
    # --------------------------------------------------------

    if image_fn > 0:

        cv2.imwrite(
            str(
                FALSE_NEGATIVE_DIR /
                output_filename
            ),
            annotated
        )

    processed += 1

    if processed % 25 == 0:

        print(
            f"Processed {processed}/"
            f"{len(records)}"
        )


# ============================================================
# FINAL METRICS
# ============================================================

precision = (
    total_tp /
    (total_tp + total_fp)
    if total_tp + total_fp > 0
    else 0
)

recall = (
    total_tp /
    (total_tp + total_fn)
    if total_tp + total_fn > 0
    else 0
)

f1 = (
    2 * precision * recall /
    (precision + recall)
    if precision + recall > 0
    else 0
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 70)
print("PREDICTION FAILURE ANALYSIS")
print("=" * 70)

print(
    f"Confidence threshold: {CONFIDENCE_THRESHOLD}"
)

print(
    f"IoU threshold:        {IOU_THRESHOLD}"
)

print()

print(
    f"True positives:       {total_tp}"
)

print(
    f"False positives:      {total_fp}"
)

print(
    f"False negatives:      {total_fn}"
)

print()

print(
    f"Precision:            {precision:.4f}"
)

print(
    f"Recall:               {recall:.4f}"
)

print(
    f"F1 Score:             {f1:.4f}"
)

print()
print("=" * 70)

print("Images saved to:")

print(
    TRUE_POSITIVE_DIR
)

print(
    FALSE_POSITIVE_DIR
)

print(
    FALSE_NEGATIVE_DIR
)

print("=" * 70)

print()
print("Analysis completed successfully.")