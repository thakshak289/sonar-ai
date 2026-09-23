import cv2
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = hf_hub_download(
    repo_id="PINGEcosystem/gv-yolo26",
    filename="weights.onnx"
)

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

print("YOLO26 model loaded successfully")
print("Input:", input_name)


# ============================================================
# SETTINGS
# ============================================================

MODEL_SIZE = 640

TILE_SIZE = 512
OVERLAP = 0.25

CONFIDENCE_THRESHOLD = 0.10
IOU_THRESHOLD = 0.50

CLASS_NAME = "Crab-Pot"


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

    union = area_a + area_b - intersection_area

    if union <= 0:
        return 0.0

    return intersection_area / union


# ============================================================
# NMS
# ============================================================

def nms(detections, iou_threshold=IOU_THRESHOLD):

    if not detections:
        return []

    detections = sorted(
        detections,
        key=lambda x: x["confidence"],
        reverse=True
    )

    selected = []

    while detections:

        best = detections.pop(0)
        selected.append(best)

        remaining = []

        for detection in detections:

            iou = calculate_iou(
                best["box"],
                detection["box"]
            )

            if iou < iou_threshold:
                remaining.append(detection)

        detections = remaining

    return selected


# ============================================================
# SINGLE TILE INFERENCE
# ============================================================

def run_tile(tile):

    tile_height, tile_width = tile.shape[:2]

    image_rgb = cv2.cvtColor(
        tile,
        cv2.COLOR_BGR2RGB
    )

    resized = cv2.resize(
        image_rgb,
        (MODEL_SIZE, MODEL_SIZE)
    )

    input_image = resized.astype(
        np.float32
    ) / 255.0

    input_image = np.transpose(
        input_image,
        (2, 0, 1)
    )

    input_image = np.expand_dims(
        input_image,
        axis=0
    )

    outputs = session.run(
        None,
        {input_name: input_image}
    )

    raw_detections = outputs[0][0]

    detections = []

    scale_x = tile_width / MODEL_SIZE
    scale_y = tile_height / MODEL_SIZE

    for detection in raw_detections:

        x1, y1, x2, y2, confidence, class_id = detection

        confidence = float(confidence)

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        x1 = max(0, min(tile_width, x1 * scale_x))
        y1 = max(0, min(tile_height, y1 * scale_y))
        x2 = max(0, min(tile_width, x2 * scale_x))
        y2 = max(0, min(tile_height, y2 * scale_y))

        if x2 <= x1 or y2 <= y1:
            continue

        detections.append({
            "box": [
                float(x1),
                float(y1),
                float(x2),
                float(y2)
            ],
            "confidence": confidence,
            "class_id": int(class_id)
        })

    return detections


# ============================================================
# TILE GENERATION
# ============================================================

def generate_tiles(image):

    height, width = image.shape[:2]

    stride = int(
        TILE_SIZE * (1 - OVERLAP)
    )

    tiles = []

    y = 0

    while y < height:

        x = 0

        y2 = min(
            y + TILE_SIZE,
            height
        )

        y1 = max(
            0,
            y2 - TILE_SIZE
        )

        while x < width:

            x2 = min(
                x + TILE_SIZE,
                width
            )

            x1 = max(
                0,
                x2 - TILE_SIZE
            )

            tile = image[
                y1:y2,
                x1:x2
            ]

            tiles.append(
                (tile, x1, y1)
            )

            if x2 >= width:
                break

            x += stride

        if y2 >= height:
            break

        y += stride

    return tiles


# ============================================================
# FULL IMAGE DETECTION
# ============================================================

def detect_image(image):

    if image is None:
        raise ValueError("Invalid image")

    original_height, original_width = image.shape[:2]

    tiles = generate_tiles(image)

    all_detections = []

    for tile, offset_x, offset_y in tiles:

        tile_detections = run_tile(tile)

        for detection in tile_detections:

            x1, y1, x2, y2 = detection["box"]

            # Convert tile coordinates
            # to original image coordinates

            x1 += offset_x
            y1 += offset_y

            x2 += offset_x
            y2 += offset_y

            x1 = max(
                0,
                min(original_width, x1)
            )

            y1 = max(
                0,
                min(original_height, y1)
            )

            x2 = max(
                0,
                min(original_width, x2)
            )

            y2 = max(
                0,
                min(original_height, y2)
            )

            all_detections.append({
                "box": [
                    x1,
                    y1,
                    x2,
                    y2
                ],
                "confidence": detection["confidence"],
                "class_id": detection["class_id"]
            })

    # Remove duplicate detections
    final_detections = nms(
        all_detections
    )

    return final_detections


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk(confidence):

    if confidence >= 0.70:
        return "HIGH"

    if confidence >= 0.40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# FORMAT RESULTS
# ============================================================

def format_detections(detections):

    results = []

    for detection in detections:

        confidence = detection["confidence"]

        results.append({
            "label": CLASS_NAME,
            "confidence": round(
                confidence,
                3
            ),
            "risk": calculate_risk(
                confidence
            ),
            "box": [
                round(float(v), 2)
                for v in detection["box"]
            ]
        })

    return results


# ============================================================
# DRAW RESULTS
# ============================================================

def draw_detections(
    image,
    detections
):

    result = image.copy()

    for detection in detections:

        x1, y1, x2, y2 = [
            int(v)
            for v in detection["box"]
        ]

        confidence = detection["confidence"]

        label = (
            f"{CLASS_NAME} "
            f"{confidence:.0%}"
        )

        cv2.rectangle(
            result,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.rectangle(
            result,
            (x1, max(0, y1 - 28)),
            (
                x1 + 150,
                y1
            ),
            (0, 255, 0),
            -1
        )

        cv2.putText(
            result,
            label,
            (x1 + 5, max(18, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            2
        )

    return result