import json
import os

import cv2
from tqdm import tqdm
from ultralytics import YOLO

# from google.colab import files
# from IPython.display import display, Image
# from google.colab import drive


def get_config():
    # 📁 CONFIG
    output_dir = os.getenv("OUTPUT_PATH", "../resources/outputs/")
    FRAME_OUTPUT_DIR = output_dir + "/" + "frames"
    COCO_OUTPUT_PATH = output_dir + "/" + "detections.json"
    FRAME_STEP = 30
    MODEL_NAME = output_dir + "/" + "yolov8n.pt"

    return FRAME_OUTPUT_DIR, COCO_OUTPUT_PATH, FRAME_STEP, MODEL_NAME


def get_video_path():
    video_dir = os.getenv("INPUT_PATH", "../resources/inputs/video-1")
    files = [f for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f))]
    if files:
        return video_dir + "/" + files[0]
    return None


def extract_frames(frame_output_dir, video_path, frame_step):
    # 🎞️ EXTRACT FRAMES
    os.makedirs(frame_output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx, saved_idx = 0, 0

    print("Extracting frames...")
    while True:
        success, frame = cap.read()
        if not success:
            break
        if frame_idx % frame_step == 0:
            cv2.imwrite(f"{frame_output_dir}/frame_{saved_idx:05d}.jpg", frame)
            saved_idx += 1
        frame_idx += 1

    cap.release()
    print(f"Saved {saved_idx} frames to {frame_output_dir}/")


def pre_tag_video(frame_output_dir, model_name):
    # 🤖 PRE-TAG WITH YOLO
    model = YOLO(model_name)
    image_files = sorted(
        [f for f in os.listdir(frame_output_dir) if f.endswith(".jpg")]
    )

    coco_output = {"images": [], "annotations": [], "categories": []}
    category_map = {}
    next_image_id = 1
    next_ann_id = 1
    next_category_id = 1

    for image_file in tqdm(image_files, desc="Pretagging"):
        img_path = os.path.join(frame_output_dir, image_file)
        results = model(img_path)[0]
        height, width = results.orig_shape

        coco_output["images"].append(
            {
                "id": next_image_id,
                "file_name": image_file,
                "height": height,
                "width": width,
            }
        )

        for det in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls_id = det
            cls_id = int(cls_id)
            label = model.names[cls_id]

            if label not in category_map:
                category_map[label] = next_category_id
                coco_output["categories"].append(
                    {"id": next_category_id, "name": label}
                )
                next_category_id += 1

            coco_output["annotations"].append(
                {
                    "id": next_ann_id,
                    "image_id": next_image_id,
                    "category_id": category_map[label],
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "area": (x2 - x1) * (y2 - y1),
                    "iscrowd": 0,
                }
            )
            next_ann_id += 1

        next_image_id += 1
    return coco_output


def save_annotations(coco_output, coco_output_path):
    # 💾 SAVE ANNOTATIONS
    with open(coco_output_path, "w") as f:
        json.dump(coco_output, f, indent=2)

    print(f"COCO-format annotations saved to {coco_output_path}")


def main():
    video_path = get_video_path()
    frame_output_dir, coco_output_path, frame_step, model_name = get_config()
    extract_frames(frame_output_dir, video_path, frame_step)
    coco_output = pre_tag_video(frame_output_dir, model_name)
    save_annotations(coco_output, coco_output_path)


if __name__ == "__main__":
   main()