import json
import os
import time

import cv2
import imagehash
from PIL import Image
from tqdm import tqdm
from ultralytics import YOLO

try:
    from utils import (
        format_logs, is_valid_video_file, output_visual_logs
    )
except ModuleNotFoundError:
    from data_generation.main_logic.utils import (
        format_logs, is_valid_video_file, output_visual_logs
    )


def get_config(config_fp: str = None):
    """
    @TODO - add logic to pass file instead of default values?
    :return: tuple of strings
    """
    # 📁 CONFIG
    output_dir = os.path.abspath(os.getenv("OUTPUT_PATH", "../resources/outputs"))

    FRAME_OUTPUT_DIR, COCO_OUTPUT_PATH, MODEL_NAME, FRAME_STEP = (
        None,
        None,
        None,
        None,
    )

    if config_fp is not None and os.path.exists(config_fp):
        """Read file contents here"""
        config_fp = os.path.abspath(config_fp)
        pass
    else:
        FRAME_OUTPUT_DIR = output_dir + "/" + "frames"
        COCO_OUTPUT_PATH = output_dir + "/" + "detections.json"
        FRAME_STEP = 30
        MODEL_NAME = output_dir + "/" + "yolov8n.pt"

    assert FRAME_OUTPUT_DIR is not None
    assert COCO_OUTPUT_PATH is not None
    assert FRAME_STEP is not None
    assert MODEL_NAME is not None

    return FRAME_OUTPUT_DIR, COCO_OUTPUT_PATH, FRAME_STEP, MODEL_NAME, output_dir


def get_video_path(output_dir, video_dir):
    """
    :return:
    """
    start_time = time.time()
    if video_dir is None or os.path.isdir(video_dir):
        video_dir = "../resources/inputs/video-1"
    video_dir = os.path.abspath(video_dir)

    files = [
        f
        for f in os.listdir(video_dir)
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
        "no valid video path found",
        time.time() - start_time,
        output_dir,
    )
    return None


def extract_frames(
    frame_output_dir, video_path, output_dir, frame_step, hash_threshold=1
):
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

    format_logs(
        "extract_frames",
        f"Extracted {frame_idx} frames",
        time.time() - start_time,
        output_dir,
    )
    format_logs(
        "extract_frames",
        f"saved {saved_idx} unique frames",
        time.time() - start_time,
        output_dir,
    )
    format_logs(
        "extract_frames",
        f"removed {duplicate_count} duplicates",
        time.time() - start_time,
        output_dir,
    )

    print(f"Saved {saved_idx} unique frames to {frame_output_dir}/")
    print(f"Removed {duplicate_count} duplicate frames.")


def pre_tag_video(frame_output_dir, model_name, output_dir):
    """
    :param frame_output_dir:
    :param model_name:
    :return:
    """
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
    format_logs(
        "pre_tag_video",
        f"Number of categories detected: {len(category_map)}",
        "NA",
        output_dir,
    )
    format_logs(
        "pre_tag_video",
        f"Class Information: {category_map}",
        "NA",
        output_dir,
    )
    return coco_output


def save_annotations(coco_output, coco_output_path, output_dir):
    """
    :param coco_output:
    :param coco_output_path:
    :return:
    """
    start_time = time.time()
    with open(coco_output_path, "w") as f:
        json.dump(coco_output, f, indent=2)

    format_logs(
        "save_annotations",
        f"COCO-format annotations saved to {coco_output_path}",
        time.time() - start_time,
        output_dir,
    )


def clean_up(dir_path):
    import shutil

    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
        print(f"Deleted directory: {dir_path}")
    else:
        print(f"Directory does not exist: {dir_path}")


def main():
    """
    :return:
    """
    start_time = time.time()
    config_fp = os.getenv("INPUT_PATH")
    video_dir = os.getenv("INPUT_PATH")

    (
        frame_output_dir,
        coco_output_path,
        frame_step,
        model_name,
        output_dir,
    ) = get_config(config_fp)
    video_path = get_video_path(output_dir, video_dir)
    extract_frames(frame_output_dir, video_path, output_dir, frame_step)
    coco_output = pre_tag_video(frame_output_dir, model_name, output_dir)
    save_annotations(coco_output, coco_output_path, output_dir)
    format_logs(
        "main function",
        "completed main function",
        time.time() - start_time,
        output_dir
    )
    output_visual_logs(output_dir)


if __name__ == "__main__":
    main()
