from pathlib import Path
import json
from collections import Counter

DATASET = Path("dataset")

print("=" * 60)
print("GHOSTVISION DATASET AUDIT")
print("=" * 60)

# --------------------------------------------------
# Find images
# --------------------------------------------------

images = list(DATASET.rglob("*.jpg"))
images += list(DATASET.rglob("*.jpeg"))
images += list(DATASET.rglob("*.png"))

print(f"\nTotal images: {len(images)}")

# --------------------------------------------------
# Show directories containing images
# --------------------------------------------------

print("\nImage directories:")

directories = Counter(str(img.parent) for img in images)

for directory, count in directories.items():
    print(f"  {directory}: {count} images")

# --------------------------------------------------
# Find annotation files
# --------------------------------------------------

jsonl_files = list(DATASET.rglob("*.jsonl"))
json_files = list(DATASET.rglob("*.json"))
txt_files = list(DATASET.rglob("*.txt"))

print("\nAnnotation files:")
print(f"  JSONL: {len(jsonl_files)}")
print(f"  JSON:  {len(json_files)}")
print(f"  TXT:   {len(txt_files)}")

for file in jsonl_files:
    print(f"  JSONL → {file}")

# --------------------------------------------------
# Analyze JSONL
# --------------------------------------------------

category_counts = Counter()
annotation_count = 0
records = 0

for file in jsonl_files:

    print(f"\nReading: {file}")

    with open(file, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            records += 1

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            objects = data.get("objects", {})

            categories = objects.get("category", [])

            for category in categories:
                category_counts[str(category)] += 1
                annotation_count += 1

print("\n" + "=" * 60)
print("ANNOTATION SUMMARY")
print("=" * 60)

print(f"\nRecords: {records}")
print(f"Total annotations: {annotation_count}")

print("\nClasses:")

for category, count in category_counts.items():
    print(f"  {category}: {count}")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)