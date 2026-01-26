import json
import os

def convert_coco(coco_json, images_dir, labels_dir):
    os.makedirs(labels_dir, exist_ok=True)

    with open(coco_json, 'r') as f:
        coco = json.load(f)

    images = {img["id"]: img for img in coco["images"]}
    categories = {cat["id"]: idx for idx, cat in enumerate(coco["categories"])}

    for ann in coco["annotations"]:
        image = images[ann["image_id"]]
        img_w, img_h = image["width"], image["height"]

        x, y, w, h = ann["bbox"]
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        w /= img_w
        h /= img_h

        class_id = categories[ann["category_id"]]

        label_path = os.path.join(
            labels_dir,
            image["file_name"].replace(".jpg", ".txt").replace(".png", ".txt")
        )

        with open(label_path, "a") as f:
            f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")


# -------- RUN FOR EACH SPLIT --------
base = "data/helmet_images"

convert_coco(
    f"{base}/train/_annotations.coco.json",
    f"{base}/train/images",
    f"{base}/train/labels"
)

convert_coco(
    f"{base}/val/_annotations.coco.json",
    f"{base}/val/images",
    f"{base}/val/labels"
)

convert_coco(
    f"{base}/test/_annotations.coco.json",
    f"{base}/test/images",
    f"{base}/test/labels"
)

print("COCO to YOLO conversion completed")
