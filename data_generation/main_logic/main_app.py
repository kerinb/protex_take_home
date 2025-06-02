import json
import os
import time

import cv2
import imagehash
from PIL import Image
from tqdm import tqdm
from ultralytics import YOLO
from utils import format_logs, is_valid_video_file

output_dir = ""


def get_config():
    """

    :return:
    """
    # 📁 CONFIG
    global output_dir
    output_dir = os.getenv("OUTPUT_PATH", "../resources/outputs")
    FRAME_OUTPUT_DIR = output_dir + "/" + "frames"
    COCO_OUTPUT_PATH = output_dir + "/" + "detections.json"
    FRAME_STEP = 30
    MODEL_NAME = output_dir + "/" + "yolov8n.pt"

    print(output_dir)
    print(FRAME_OUTPUT_DIR)
    print(COCO_OUTPUT_PATH)
    print(MODEL_NAME)
    print(os.curdir)
    return FRAME_OUTPUT_DIR, COCO_OUTPUT_PATH, FRAME_STEP, MODEL_NAME


def get_video_path():
    """

    :return:
    """
    start_time = time.time()
    video_dir = os.getenv("INPUT_PATH", "../resources/inputs/video-1")
    files = [
        f for f in os.listdir(video_dir)
        if os.path.isfile(os.path.join(video_dir, f)) and is_valid_video_file(f)
    ]
    if files:
        vid_path = video_dir + "/" + files[0]
        format_logs(
            "get_video_path",
            f"found video in path: {vid_path}",
            time.time() - start_time,
            output_dir,
        )
        return vid_path
    format_logs(
        "get_video_path",
        f"no valid video path found",
        time.time() - start_time,
        output_dir,
    )
    return None


def frame_to_hash(frame):
    """

    :param frame:
    :return:
    """
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return imagehash.phash(pil_image)


def extract_frames(frame_output_dir, video_path, frame_step, hash_threshold=10):
    """

    :param frame_output_dir:
    :param video_path:
    :param frame_step:
    :param hash_threshold:
    :return:
    """
    os.makedirs(frame_output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx, saved_idx, duplicate_count = 0, 0, 0
    saved_hashes = []

    print("Extracting frames...")
    start_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_idx % frame_step == 0:
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            curr_hash = imagehash.phash(pil_img)

            # Check if curr_hash is similar to any saved hash
            is_dup = False
            for h in saved_hashes:
                if abs(curr_hash - h) <= hash_threshold:
                    is_dup = True
                    break

            if not is_dup:
                cv2.imwrite(f"{frame_output_dir}/frame_{saved_idx:05d}.jpg", frame)
                saved_hashes.append(curr_hash)
                saved_idx += 1
            else:
                duplicate_count += 1

        frame_idx += 1

    cap.release()

    # Log once after finishing
    format_logs(
        "extract_frames",
        f"Extracted {frame_idx} frames, saved {saved_idx} unique frames, removed {duplicate_count} duplicates",
        time.time() - start_time,
        output_dir,
    )

    print(f"Saved {saved_idx} unique frames to {frame_output_dir}/")
    print(f"Removed {duplicate_count} duplicate frames.")


def pre_tag_video(frame_output_dir, model_name):
    """

    :param frame_output_dir:
    :param model_name:
    :return:
    """
    # 🤖 PRE-TAG WITH YOLO
    start_time = time.time()
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
    format_logs(
        "pre_tag_video",
        f"Images processed: {next_image_id}",
        time.time() - start_time,
        output_dir,
    )

    return coco_output


def save_annotations(coco_output, coco_output_path):
    """

    :param coco_output:
    :param coco_output_path:
    :return:
    """
    # 💾 SAVE ANNOTATIONS
    with open(coco_output_path, "w") as f:
        json.dump(coco_output, f, indent=2)

    print(f"COCO-format annotations saved to {coco_output_path}")


def main():
    """

    :return:
    """
    frame_output_dir, coco_output_path, frame_step, model_name = get_config()
    video_path = get_video_path()
    extract_frames(frame_output_dir, video_path, frame_step)
    coco_output = pre_tag_video(frame_output_dir, model_name)
    save_annotations(coco_output, coco_output_path)


if __name__ == "__main__":
    main()
