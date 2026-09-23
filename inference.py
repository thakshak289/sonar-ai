import os
import cv2
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download


# --------------------------------------------------
# 1. Download / locate model
# --------------------------------------------------

MODEL_PATH = hf_hub_download(
    repo_id="PINGEcosystem/gv-yolo26",
    filename="weights.onnx"
)

# --------------------------------------------------
# 2. Load ONNX model
# --------------------------------------------------

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

print("Model loaded successfully")
print("Input:", input_name)


# --------------------------------------------------
# 3. Load image
# --------------------------------------------------

IMAGE_PATH = "test_images/test.jpg"

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Could not find image: {IMAGE_PATH}"
    )

original = image.copy()

original_height, original_width = image.shape[:2]

print("Original image size:",
      original_width, "x", original_height)


# --------------------------------------------------
# 4. Preprocess
# --------------------------------------------------

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image_resized = cv2.resize(
    image_rgb,
    (640, 640)
)

image_input = image_resized.astype(
    np.float32
) / 255.0

# HWC -> CHW
image_input = np.transpose(
    image_input,
    (2, 0, 1)
)

# Add batch dimension
image_input = np.expand_dims(
    image_input,
    axis=0
)


# --------------------------------------------------
# 5. Run inference
# --------------------------------------------------

outputs = session.run(
    None,
    {input_name: image_input}
)

detections = outputs[0][0]

print("\nRaw detections shape:")
print(detections.shape)


# --------------------------------------------------
# 6. Process detections
# --------------------------------------------------

CONFIDENCE_THRESHOLD = 0.25

count = 0

for detection in detections:

    x1, y1, x2, y2, confidence, class_id = detection

    if confidence < CONFIDENCE_THRESHOLD:
        continue

    count += 1

    # Convert 640x640 coordinates
    # back to original image size

    x1 = int(x1 * original_width / 640)
    y1 = int(y1 * original_height / 640)
    x2 = int(x2 * original_width / 640)
    y2 = int(y2 * original_height / 640)

    class_id = int(class_id)

    print(
        f"Detection {count}: "
        f"class={class_id}, "
        f"confidence={confidence:.3f}, "
        f"box=({x1}, {y1}, {x2}, {y2})"
    )

    # Draw bounding box

    cv2.rectangle(
        original,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    label = f"Crab-Pot {confidence:.2f}"

    cv2.putText(
        original,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )


# --------------------------------------------------
# 7. Save result
# --------------------------------------------------

os.makedirs("outputs", exist_ok=True)

output_path = "outputs/result.jpg"

cv2.imwrite(
    output_path,
    original
)

print("\n--------------------------------")
print(f"Detections: {count}")
print(f"Result saved to: {output_path}")
print("--------------------------------")